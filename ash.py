import streamlit as st
import psutil
import pandas as pd
import plotly.express as px
import time
import platform
from datetime import datetime

# --------------------- Streamlit Page Config ---------------------
st.set_page_config(page_title='Real-Time Monitoring Dashboard', layout='wide')

# Custom Styling
st.markdown("""
    <style>
        .main { background-color: #f4f4f4; }
        h1 { text-align: center; color: #333; }
        .css-1aumxhk { display: none }  /* Hide footer */
       /* Style for the sidebar */
        [data-testid="stSidebar"] {
            background-color: #1E1E2E !important;
            border-radius: 12px;
            padding: 15px;
        }

        /* Sidebar Header */
        .sidebar-title {
            font-size: 24px;
            font-weight: bold;
            color: #ffffff;
            text-align: center;
            margin-bottom: 20px;
        }

        /* Style for radio buttons */
        div[data-testid="stRadio"] div {
            background-color: #34344A;
            border-radius: 10px;
            padding: 12px 10px !important;
            text-align: center;
            font-size: 18px !important;
            color: white !important;
            transition: 0.3s;
            margin-bottom: 8px;
        }

        /* Hover effect */
        div[data-testid="stRadio"] div:hover {
            background-color: #6C63FF;
            cursor: pointer;
            transform: scale(1.05);
        }

        /* Selected radio button */
        div[data-testid="stRadio"] div[aria-checked="true"] {
            background-color: #6C63FF !important;
            font-weight: bold !important;
            border-left: 5px solid #FFD700;
        }
    </style>
""", unsafe_allow_html=True)

st.title("🔍 Real-Time System Monitoring Dashboard")

# --------------------- Function to Fetch System Stats ---------------------
def get_system_stats():
    return {
        "CPU Usage (%)": psutil.cpu_percent(interval=1),
        "Memory Usage (%)": psutil.virtual_memory().percent,
        "Available Memory (MB)": round(psutil.virtual_memory().available / (1024 * 1024), 2),
        "Disk Usage (%)": psutil.disk_usage('/').percent,
        "Network Sent (MB)": round(psutil.net_io_counters().bytes_sent / (1024 * 1024), 2),
        "Network Received (MB)": round(psutil.net_io_counters().bytes_recv / (1024 * 1024), 2)
    }

# --------------------- Sidebar Navigation ---------------------
st.sidebar.header("📌 Select a Module")
st.markdown('<p class="sidebar-title">📌 Select a Module</p>', unsafe_allow_html=True)

menu = st.sidebar.radio(
    "Navigate to:",
    ["Live CPU & Memory", "Active Processes", "Terminate Process", "Terminated Processes Log", "Disk Usage", "Network Usage"]
)

# ================= MODULE 1: Live CPU & Memory Usage ===================
if menu == "Live CPU & Memory":
    st.subheader("🔘 Live CPU & Memory Usage")
    chart_container = st.empty()
    stats_container = st.empty()
    data = []
    
    st.subheader("🔘 Live Resource Usage Over Time")
    while True:
        stats = get_system_stats()
        data.append(stats)
        df = pd.DataFrame(data)

        stats_container.metric("CPU Usage (%)", stats["CPU Usage (%)"])
        stats_container.metric("Memory Usage (%)", stats["Memory Usage (%)"])

        fig = px.line(df, y=["CPU Usage (%)", "Memory Usage (%)", "Disk Usage (%)"],
                      labels={"index": "Time"},
                      title="Resource Usage Over Time")

        chart_container.plotly_chart(fig, use_container_width=True)
        time.sleep(1)

# ================= MODULE 2: Active Processes ===================
elif menu == "Active Processes":
    st.subheader("🔘️ Active Processes Monitor")

    # Fetch process data
    def get_processes():
        process_data = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
            process_data.append(proc.info)
        return pd.DataFrame(process_data).sort_values(by='cpu_percent', ascending=False)

    df_processes = get_processes()

    # Custom Styling
    st.markdown("""
        <style>
            .process-table th { background-color: #0066cc; color: white; text-align: center; }
            .process-table td { text-align: center; }
            .highlight { font-weight: bold; color: #0077b6; }
        </style>
    """, unsafe_allow_html=True)

    # Display Process Data
    if not df_processes.empty:
        st.markdown("### 📋 Running Processes")

        # **Interactive Filtering**
        search_text = st.text_input("🔍 Search Process by Name")
        if search_text:
            df_processes = df_processes[df_processes["name"].str.contains(search_text, case=False, na=False)]

        # **Improved Table Display with Progress Bars**
        st.write("### 🔘 CPU & Memory Usage")
        for index, row in df_processes.iterrows():
            with st.expander(f"🔹 {row['name']} (PID: {row['pid']})"):
                st.progress(min(100, int(row['cpu_percent'])), text=f"🔥 CPU: {row['cpu_percent']}%")
                st.progress(min(100, int(row['memory_percent'])), text=f"💾 Memory: {row['memory_percent']}%")

                st.write(f"**PID:** `{row['pid']}`")
                st.write(f"**CPU Usage:** `{row['cpu_percent']}%`")
                st.write(f"**Memory Usage:** `{row['memory_percent']}%`")
                st.write("---")

    else:
        # **Alert Box if No Active Processes Found**
        st.markdown("""
            <div style="padding: 15px; background-color: #e6f2ff; color: #005580; border-radius: 8px; text-align: center;">
                💤 No active processes found! Try running some applications.
            </div>
        """, unsafe_allow_html=True)


# ================= MODULE 3: Terminate a Process ===================
elif menu == "Terminate Process":
    st.subheader("❌ Terminate a Process")

    # Input fields for PID and Process Name
    pid_to_kill = st.text_input("Enter Process ID (PID) to Terminate:")
    process_name_to_kill = st.text_input("Enter Process Name to Terminate:")

    # Initialize session state for terminated processes
    if "terminated_processes" not in st.session_state:
        st.session_state.terminated_processes = []

    # Terminate by PID
    if st.button("Terminate by PID"):
        if pid_to_kill:
            try:
                pid = int(pid_to_kill)
                proc = psutil.Process(pid)
                st.session_state.terminated_processes.append(
                    {"PID": pid, "Name": proc.name(), "Terminated At": datetime.now().strftime("%H:%M:%S")}
                )
                proc.terminate()
                st.success(f"✅ Process {pid} ({proc.name()}) terminated successfully!")
            except (psutil.NoSuchProcess, ValueError):
                st.error("⚠️ Invalid PID or Process does not exist!")

    # Terminate by Process Name
    if st.button("Terminate by Name"):
        if process_name_to_kill:
            found = False
            for proc in psutil.process_iter(['pid', 'name']):
                if proc.info['name'].lower() == process_name_to_kill.lower():
                    try:
                        st.session_state.terminated_processes.append(
                            {"PID": proc.info['pid'], "Name": proc.info['name'], "Terminated At": datetime.now().strftime("%H:%M:%S")}
                        )
                        psutil.Process(proc.info['pid']).terminate()
                        st.success(f"✅ Process {proc.info['pid']} ({proc.info['name']}) terminated successfully!")
                        found = True
                    except psutil.NoSuchProcess:
                        pass
            if not found:
                st.error(f"⚠️ No running process found with name '{process_name_to_kill}'.")

# ================= MODULE 4: Terminated Processes Log ===================
elif menu == "Terminated Processes Log":
    st.subheader("🔘️ Terminated Processes Log")

    if st.session_state.terminated_processes:
        df_terminated = pd.DataFrame(st.session_state.terminated_processes)

        # Add Colors & Formatting
        st.markdown("""
            <style>
                .terminated-table th { background-color: #ff4d4d; color: white; text-align: center; }
                .terminated-table td { text-align: center; }
            </style>
        """, unsafe_allow_html=True)

        st.markdown("#### 🔘 Recently Terminated Processes")
        st.dataframe(df_terminated.style.set_properties(
            **{'background-color': '#ffeeee', 'border-color': 'red', 'text-align': 'center'}
        ), use_container_width=True)

    else:
        # Fancy Alert Box for No Data
        st.markdown("""
            <div style="padding: 15px; background-color: #ffe6e6; color: #cc0000; border-radius: 8px; text-align: center;">
                🚨 No processes have been terminated yet!  
                Try terminating a process and check here for logs.
            </div>
        """, unsafe_allow_html=True)


# ==# ================= MODULE 5: Enhanced Disk Usage ===================
elif menu == "Disk Usage":
    st.subheader("🔘 Disk Usage")

    # Fetch disk statistics
    disk_info = psutil.disk_usage('/')
    disk_io = psutil.disk_io_counters()

    # Display key metrics
    disk_data = {
        "Total Disk Space (GB)": round(disk_info.total / (1024**3), 2),
        "Used Disk Space (GB)": round(disk_info.used / (1024**3), 2),
        "Free Disk Space (GB)": round(disk_info.free / (1024**3), 2),
        "Disk Usage (%)": disk_info.percent,
        "Read Speed (MB/s)": round(disk_io.read_bytes / (1024**2), 2),
        "Write Speed (MB/s)": round(disk_io.write_bytes / (1024**2), 2),
        "Read Count": disk_io.read_count,
        "Write Count": disk_io.write_count,
        "Disk I/O (Operations)": disk_io.read_count + disk_io.write_count
    }
    
    st.table(pd.DataFrame([disk_data]))

    # Display Mounted Partitions
    st.subheader("🔘 Mounted Partitions & File System Types")
    partition_data = []
    
    for partition in psutil.disk_partitions():
        partition_data.append({
            "Device": partition.device,
            "Mount Point": partition.mountpoint,
            "File System": partition.fstype,
            "Options": partition.opts
        })
    
    df_partitions = pd.DataFrame(partition_data)
    st.dataframe(df_partitions, use_container_width=True)

# ================= MODULE 6: Enhanced Network Usage ===================
elif menu == "Network Usage":
    st.subheader("🌐 Network Usage")

    # Fetch network statistics
    net_io = psutil.net_io_counters()
    net_if_addrs = psutil.net_if_addrs()
    net_if_stats = psutil.net_if_stats()

    # Display key metrics
    network_data = {
        "Bytes Sent (MB)": round(net_io.bytes_sent / (1024 * 1024), 2),
        "Bytes Received (MB)": round(net_io.bytes_recv / (1024 * 1024), 2),
        "Packets Sent": net_io.packets_sent,
        "Packets Received": net_io.packets_recv,
        "Transmission Errors": net_io.errout,
        "Reception Errors": net_io.errin,
        "Dropped Packets Sent": net_io.dropout,
        "Dropped Packets Received": net_io.dropin
    }
    
    st.table(pd.DataFrame([network_data]))

    # Display Network Interface Information
    st.subheader("🛜 Active Network Interfaces")
    interface_data = []
    
    for interface, stats in net_if_stats.items():
        interface_data.append({
            "Interface": interface,
            "Is Up": "✅ Yes" if stats.isup else "❌ No",
            "Speed (Mbps)": stats.speed if stats.speed > 0 else "Unknown",
            "MTU": stats.mtu
        })
    
    df_interfaces = pd.DataFrame(interface_data)
    st.dataframe(df_interfaces, use_container_width=True)
