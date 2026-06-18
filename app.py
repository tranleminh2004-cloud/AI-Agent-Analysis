import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ==============================================================================
# 1. CẤU HÌNH TRANG & GIAO DIỆN CHUNG
# ==============================================================================
st.set_page_config(
    page_title="CS AI Agent Analysis Dashboard", 
    layout="wide", 
    initial_sidebar_state="expanded",
    page_icon="🤖"
)

# Tùy chỉnh CSS tạo điểm nhấn chuyên nghiệp
st.markdown("""
    <style>
    .main .block-container { padding-top: 1.5rem; padding-bottom: 2rem; }
    h1 { color: #1E3A8A; font-weight: 700; margin-bottom: 0px; }
    h2 { color: #0F172A; border-left: 5px solid #2563EB; padding-left: 12px; margin-top: 20px; }
    div[data-testid="metric-container"] {
        background-color: #F8FAFC;
        padding: 15px;
        border-radius: 8px;
        border: 1px solid #E2E8F0;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        transition: transform 0.2s;
    }
    div[data-testid="metric-container"]:hover {
        transform: translateY(-5px);
    }
    </style>
""", unsafe_allow_html=True)

# ==============================================================================
# 2. HÀM ĐỌC VÀ LÀM SẠCH DỮ LIỆU TỪ 4 FILE
# ==============================================================================
@st.cache_data
def load_data():
    try:
        df_meta = pd.read_csv("domain_worker_metadata.csv")
        df_desire = pd.read_csv("domain_worker_desires.csv")
        df_expert = pd.read_csv("expert_rated_technological_capability.csv")
        df_task = pd.read_csv("task_statement_with_metadata.csv") # FILE MỚI
        
        # Làm sạch khoảng trắng trong tên cột
        for df in [df_meta, df_desire, df_expert, df_task]:
            df.columns = df.columns.str.strip()
        
        # Từ khóa lọc nhóm ngành CNTT / Khoa học máy tính
        keywords = 'Computer|Software|Developer|Programmer|Database|Network|Security|Data Analyst|Information Systems'
        
        cs_meta = df_meta[df_meta['Occupation (O*NET-SOC Title)'].str.contains(keywords, case=False, na=False)]
        cs_desire = df_desire[df_desire['Occupation (O*NET-SOC Title)'].str.contains(keywords, case=False, na=False)]
        cs_expert = df_expert[df_expert['Occupation (O*NET-SOC Title)'].str.contains(keywords, case=False, na=False)]
        cs_task = df_task[df_task['Occupation (O*NET-SOC Title)'].str.contains(keywords, case=False, na=False)]
        
        return cs_meta, cs_desire, cs_expert, cs_task, None
    except Exception as e:
        return None, None, None, None, str(e)

cs_meta, cs_desire, cs_expert, cs_task, error_msg = load_data()

# ==============================================================================
# 3. THIẾT KẾ SIDEBAR (THANH ĐIỀU HƯỚNG & BỘ LỌC ĐỘNG)
# ==============================================================================
with st.sidebar:
    st.title("💻 Menu Hệ Thống")
    st.markdown("---")
    
    page = st.radio(
        "Vui lòng chọn hạng mục báo cáo:",
        [
            "📊 1. Thực trạng Sử dụng AI", 
            "💡 2. Nhu cầu Tự động hóa", 
            "🧠 3. Đánh giá từ Chuyên gia",
            "🚀 4. Đề xuất Chiến lược (Toàn diện)"
        ],  
        index=0
    )
    st.markdown("---")
    
    if not error_msg:
        st.subheader("⚙️ Bộ lọc dữ liệu nâng cao")
        all_occupations = sorted(list(set(cs_meta['Occupation (O*NET-SOC Title)'].unique())))
        selected_jobs = st.multiselect(
            "Lọc theo Vị trí Chuyên môn:",
            options=all_occupations,
            default=[],
            placeholder="Để trống = Hiện tất cả",
            help="Hệ thống sẽ cập nhật toàn bộ biểu đồ theo vị trí bạn chọn."
        )
        
        # Lọc dữ liệu theo tùy chọn
        jobs_to_filter = selected_jobs if selected_jobs else all_occupations
        filtered_meta = cs_meta[cs_meta['Occupation (O*NET-SOC Title)'].isin(jobs_to_filter)]
        filtered_desire = cs_desire[cs_desire['Occupation (O*NET-SOC Title)'].isin(jobs_to_filter)]
        filtered_expert = cs_expert[cs_expert['Occupation (O*NET-SOC Title)'].isin(jobs_to_filter)]
        filtered_task = cs_task[cs_task['Occupation (O*NET-SOC Title)'].isin(jobs_to_filter)]
    
    st.markdown("---")
    st.info("**Nguồn dữ liệu:** Tích hợp từ 4 tập dữ liệu O*NET và khảo sát AI của WorkBank.")

# ==============================================================================
# 4. NỘI DUNG CHÍNH CỦA BÁO CÁO
# ==============================================================================
if error_msg:
    st.error(f"❌ Lỗi đọc file: {error_msg}. Đảm bảo 4 file CSV đang ở cùng thư mục.")
else:
    st.title("💻 Báo cáo Ứng dụng AI Agent ngành Khoa học Máy tính")
    if len(jobs_to_filter) == len(all_occupations):
        st.markdown("*Phạm vi: Toàn bộ nhóm ngành Khoa học máy tính & CNTT*")
    else:
        st.markdown(f"*Phạm vi: {len(jobs_to_filter)} vị trí chuyên môn đã chọn*")
    st.markdown("---")
    
    # --------------------------------------------------------------------------
    # TRANG 1: THỰC TRẠNG SỬ DỤNG AI
    # --------------------------------------------------------------------------
    if page == "📊 1. Thực trạng Sử dụng AI":
        st.header("Tần suất nhân sự IT sử dụng LLM/AI vào công việc")
        
        col_m1, col_m2, col_m3 = st.columns(3)
        col_m1.metric("Tổng lượng nhân sự khảo sát", f"{len(filtered_meta)} người")
        col_m2.metric("Số lượng chức danh IT", filtered_meta['Occupation (O*NET-SOC Title)'].nunique())
        
        # Tính tỷ lệ người dùng AI thường xuyên (Daily/Weekly)
        if 'LLM Use in Work' in filtered_meta.columns:
            ai_users = len(filtered_meta[filtered_meta['LLM Use in Work'].str.contains('Weekly|Daily', case=False, na=False)])
            ai_rate = (ai_users / len(filtered_meta)) * 100 if len(filtered_meta) > 0 else 0
            col_m3.metric("Tỷ lệ sử dụng AI mức cao", f"{ai_rate:.1f}%", "Sử dụng hàng tuần/hàng ngày")
            
        st.markdown("<br>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns(3)
        
        def plot_llm_usage(df, column_name, title_text, color_scale):
            if column_name in df.columns and not df.empty:
                counts = df[column_name].value_counts().reset_index()
                counts.columns = ['Mức độ', 'Số lượng']
                fig = px.bar(counts, x='Số lượng', y='Mức độ', orientation='h',
                             color='Số lượng', color_continuous_scale=color_scale, text_auto=True)
                fig.update_layout(title=title_text, showlegend=False, coloraxis_showscale=False, 
                                  height=300, yaxis={'categoryorder':'total ascending'})
                return fig
            return None

        with col1:
            fig1 = plot_llm_usage(filtered_meta, 'LLM Usage by Type - Coding', "Coding", 'Blues')
            if fig1: st.plotly_chart(fig1, use_container_width=True)
        with col2:
            fig2 = plot_llm_usage(filtered_meta, 'LLM Usage by Type - System Design', "System Design", 'Tealgrn')
            if fig2: st.plotly_chart(fig2, use_container_width=True)
        with col3:
            fig3 = plot_llm_usage(filtered_meta, 'LLM Usage by Type - Data Processing', "Data Processing", 'Purples')
            if fig3: st.plotly_chart(fig3, use_container_width=True)

    # --------------------------------------------------------------------------
    # TRANG 2: NHU CẦU TỰ ĐỘNG HÓA
    # --------------------------------------------------------------------------
    elif page == "💡 2. Nhu cầu Tự động hóa":
        st.header("Các tác vụ nhân sự IT 'khao khát' giao cho AI nhất")
        
        if not filtered_desire.empty:
            task_stats = filtered_desire.groupby('Task')[['Automation Desire Rating', 'Enjoyment Rating']].mean().reset_index()
            top_tasks = task_stats.sort_values(by='Automation Desire Rating', ascending=False).head(10)
            
            fig_bar = px.bar(top_tasks, x='Automation Desire Rating', y='Task', orientation='h',
                             color='Automation Desire Rating', color_continuous_scale='Reds')
            fig_bar.update_layout(yaxis={'categoryorder':'total ascending'}, height=400, coloraxis_showscale=False)
            st.plotly_chart(fig_bar, use_container_width=True)
            
            st.subheader("📉 Tương quan: Mong muốn Tự động hóa vs Sự thích thú")
            fig_line = go.Figure()
            fig_line.add_trace(go.Scatter(x=top_tasks['Task'], y=top_tasks['Automation Desire Rating'],
                                          mode='lines+markers', name='Desire (Muốn AI làm)', line=dict(color='#DC2626', width=3)))
            fig_line.add_trace(go.Scatter(x=top_tasks['Task'], y=top_tasks['Enjoyment Rating'],
                                          mode='lines+markers', name='Enjoyment (Thích làm)', line=dict(color='#10B981', width=3, dash='dash')))
            fig_line.update_layout(xaxis_tickangle=-25, height=450, legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
            st.plotly_chart(fig_line, use_container_width=True)

    # --------------------------------------------------------------------------
    # TRANG 3: ĐÁNH GIÁ CHUYÊN GIA
    # --------------------------------------------------------------------------
    elif page == "🧠 3. Đánh giá từ Chuyên gia":
        st.header("Đánh giá Năng lực Thực tế của AI Agent")
        
        if not filtered_expert.empty:
            expert_stats = filtered_expert.groupby('Task')[['Automation Capacity Rating', 'Human Agency Scale Rating']].mean().reset_index()
            
            st.subheader("📉 Ma trận Phân Vị: Năng lực AI vs Sự giám sát của con người")
            fig_scatter = px.scatter(expert_stats, x='Automation Capacity Rating', y='Human Agency Scale Rating',
                                     hover_name='Task', color='Automation Capacity Rating', 
                                     color_continuous_scale='Viridis', size_max=12,
                                     labels={'Automation Capacity Rating': 'Năng lực AI (Capacity)',
                                             'Human Agency Scale Rating': 'Mức độ Can thiệp (Human Agency)'})
            fig_scatter.add_shape(type="line", x0=3.0, y0=0, x1=3.0, y1=5, line=dict(color="#EF4444", dash="dash"))
            fig_scatter.add_shape(type="line", x0=0, y0=2.5, x1=5, y1=2.5, line=dict(color="#EF4444", dash="dash"))
            fig_scatter.update_layout(height=500)
            st.plotly_chart(fig_scatter, use_container_width=True)
            
            st.markdown("*Lưu ý: Góc dưới bên phải (Năng lực AI cao + Can thiệp ít) là điểm 'ngọt' nhất để tự động hóa.*")

   # --------------------------------------------------------------------------
    # TRANG 4: ĐỀ XUẤT CHIẾN LƯỢC TỔNG HỢP (KẾT HỢP FILE THỨ 4)
    # --------------------------------------------------------------------------
    elif page == "🚀 4. Đề xuất Chiến lược (Toàn diện)":
        st.header("Chiến lược Tối ưu hóa: Năng lực AI vs Mức độ Quan trọng của Tác vụ")
        st.markdown("Phân tích này kết hợp đánh giá khả năng công nghệ (từ chuyên gia) và chỉ số tính chất công việc **(Mức độ quan trọng - Importance & Mức lương bình quân - Wage)** từ O*NET.")
        
        if not filtered_task.empty and not filtered_expert.empty:
            if 'Task' in filtered_expert.columns and 'Task' in filtered_task.columns:
                
                # 1. Tính trung bình năng lực AI theo tên Tác vụ
                expert_agg = filtered_expert.groupby('Task', as_index=False)['Automation Capacity Rating'].mean()
                
                # 2. Lấy thông tin mức độ quan trọng và lương theo tên Tác vụ
                task_agg = filtered_task.groupby('Task', as_index=False).agg({
                    'Importance': 'mean',
                    'Occupation Mean Annual Wage': 'mean'
                })
                
                # 3. Gộp 2 bảng lại với nhau dựa trên cột 'Task'
                merged_df = pd.merge(expert_agg, task_agg, on='Task', how='inner')
                
                if not merged_df.empty:
                    # ---> ĐÂY LÀ DÒNG FIX LỖI QUAN TRỌNG NHẤT <---
                    # Xử lý các tác vụ bị thiếu thông tin lương (NaN) để biểu đồ Plotly không bị lỗi
                    mean_wage = merged_df['Occupation Mean Annual Wage'].mean()
                    fill_value = mean_wage if not pd.isna(mean_wage) else 100000 
                    merged_df['Occupation Mean Annual Wage'] = merged_df['Occupation Mean Annual Wage'].fillna(fill_value)
                    # -----------------------------------------------

                    col_w1, col_w2 = st.columns(2)
                    col_w1.metric("Mức lương trung bình của nhóm phân tích", f"${fill_value:,.0f} / năm")
                    col_w2.metric("Số lượng tác vụ lõi được map thành công", f"{len(merged_df)} tác vụ")
                    
                    st.subheader("🎯 Ma trận Ưu tiên: Tầm quan trọng (Importance) vs Năng lực AI (Capacity)")
                    st.markdown("Xác định đâu là những **Tác vụ Quan trọng nhất (Lõi)** mà AI **có khả năng thay thế tốt nhất**.")
                    
                    # Vẽ Scatter Plot bubble với Size là mức lương
                    fig_matrix = px.scatter(
                        merged_df, 
                        x='Importance', 
                        y='Automation Capacity Rating',
                        size='Occupation Mean Annual Wage',
                        color='Automation Capacity Rating',
                        hover_name='Task',
                        color_continuous_scale='Turbo',
                        labels={
                            'Importance': 'Mức độ Quan trọng của Công việc',
                            'Automation Capacity Rating': 'Năng lực AI giải quyết',
                            'Occupation Mean Annual Wage': 'Mức lương'
                        }
                    )
                    
                    # Chia vạch trung vị cho ma trận
                    med_imp = merged_df['Importance'].median()
                    med_cap = merged_df['Automation Capacity Rating'].median()
                    fig_matrix.add_hline(y=med_cap, line_dash="dot", line_color="red")
                    fig_matrix.add_vline(x=med_imp, line_dash="dot", line_color="red")
                    
                    # Ghi chú vùng Quadrant
                    fig_matrix.add_annotation(x=merged_df['Importance'].max(), y=merged_df['Automation Capacity Rating'].max(),
                                              text="🌟 QUAN TRỌNG & DỄ TỰ ĐỘNG HÓA", showarrow=False, font=dict(color="green", size=12))
                    
                    fig_matrix.update_layout(height=600, plot_bgcolor='rgba(0,0,0,0)', xaxis=dict(showgrid=True, gridcolor='#e2e8f0'), yaxis=dict(showgrid=True, gridcolor='#e2e8f0'))
                    st.plotly_chart(fig_matrix, use_container_width=True)
                    
                    st.markdown("---")
                    st.subheader("📋 Bảng Đề Xuất Ưu Tiên Triển Khai AI Agent")
                    
                    # Lọc ra các tác vụ có Importance cao và AI Capacity cũng cao
                    top_targets = merged_df[(merged_df['Importance'] >= med_imp) & (merged_df['Automation Capacity Rating'] >= med_cap)]
                    st.dataframe(top_targets.sort_values(by='Automation Capacity Rating', ascending=False)[['Task', 'Automation Capacity Rating', 'Importance', 'Occupation Mean Annual Wage']].head(10), use_container_width=True)
                    
                else:
                    st.warning("⚠️ Chưa tìm thấy sự trùng khớp tên tác vụ (Task).")
            else:
                st.error("⚠️ Dữ liệu bị thiếu cột 'Task'.")
