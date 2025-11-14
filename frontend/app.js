// API基础URL（从config.js加载，如果不存在则使用默认值）
const API_BASE = (typeof window !== 'undefined' && window.API_BASE) 
    ? window.API_BASE 
    : 'http://localhost:5001/api';

// 初始化FullPage.js
let fullpage_api;
document.addEventListener('DOMContentLoaded', function() {
    fullpage_api = new fullpage('#fullpage', {
        licenseKey: 'gplv3-license',
        navigation: true,
        navigationPosition: 'right',
        scrollingSpeed: 700,
        parallax: true,
        // 为第4个section（县域详情）启用内部滚动
        scrollOverflow: true,
        scrollOverflowOptions: {
            scrollbars: true,
            mouseWheel: true,
            hideScrollbars: false,
            fadeScrollbars: false
        },
        // 指定使用正常滚动的元素（避免触发fullpage切换）
        normalScrollElements: '#county-detail-content, #counties-container, #interviews-container, #county-selector-list',
        onLeave: function(origin, destination, direction) {
            // 视差效果
            const parallaxElements = destination.item.querySelectorAll('.parallax-element');
            parallaxElements.forEach(el => {
                el.style.transform = 'translateY(0)';
            });
        }
    });
    
    // 加载初始数据
    loadOverviewStats();
    loadProvinces();
    loadCounties();
});

// 加载概览统计
async function loadOverviewStats() {
    try {
        const response = await fetch(`${API_BASE}/stats/overview`);
        const result = await response.json();
        
        if (result.success) {
            const stats = result.data;
            const container = document.getElementById('stats-container');
            
            container.innerHTML = `
                <div class="bg-white/10 rounded-xl p-6 card-hover">
                    <div class="text-5xl font-black mb-2 text-indigo-400">${stats.poverty_counties}</div>
                    <div class="text-lg opacity-70">贫困县总数</div>
                </div>
                <div class="bg-white/10 rounded-xl p-6 card-hover">
                    <div class="text-5xl font-black mb-2 text-purple-400">${stats.exited_counties}</div>
                    <div class="text-lg opacity-70">已摘帽县数</div>
                </div>
                <div class="bg-white/10 rounded-xl p-6 card-hover">
                    <div class="text-5xl font-black mb-2 text-pink-400">${stats.interviews}</div>
                    <div class="text-lg opacity-70">访谈记录</div>
                </div>
                <div class="bg-white/10 rounded-xl p-6 card-hover">
                    <div class="text-5xl font-black mb-2 text-green-400">${stats.surveyors}</div>
                    <div class="text-lg opacity-70">调研员</div>
                </div>
            `;
        }
    } catch (error) {
        console.error('加载统计数据失败:', error);
    }
}

// 加载省份列表
async function loadProvinces() {
    try {
        const response = await fetch(`${API_BASE}/counties`);
        const result = await response.json();
        
        if (result.success) {
            // 获取所有唯一的省份
            const provinces = [...new Set(result.data
                .filter(c => c.Province && c.Province !== '未知')
                .map(c => c.Province)
            )].sort();
            
            const select = document.getElementById('province-filter');
            if (select) {
                // 保留"全部省份"选项
                const allOption = select.querySelector('option[value=""]');
                select.innerHTML = '';
                if (allOption) select.appendChild(allOption);
                
                // 添加省份选项
                provinces.forEach(province => {
                    const option = document.createElement('option');
                    option.value = province;
                    option.textContent = province;
                    select.appendChild(option);
                });
            }
        }
    } catch (error) {
        console.error('加载省份列表失败:', error);
    }
}

// 加载县列表
async function loadCounties(filters = {}) {
    try {
        const params = new URLSearchParams();
        if (filters.region) params.append('region', filters.region);
        if (filters.province) params.append('province', filters.province);
        
        const response = await fetch(`${API_BASE}/counties?${params}`);
        const result = await response.json();
        
        if (result.success) {
            const container = document.getElementById('counties-container');
            // 过滤掉只有最小记录的县（CountyName以"县代码"开头的），优先显示有完整数据的县
            const validCounties = result.data.filter(county => 
                county.CountyName && !county.CountyName.startsWith('县代码')
            );
            
            // 按数据完整性、摘帽时间排序，优先显示数据完整的县
            validCounties.sort((a, b) => {
                // 优先按数据完整性排序
                const aCompleteness = a.DataCompleteness || 0;
                const bCompleteness = b.DataCompleteness || 0;
                if (aCompleteness !== bCompleteness) return bCompleteness - aCompleteness;
                // 然后按摘帽时间
                if (a.ExitYear && !b.ExitYear) return -1;
                if (!a.ExitYear && b.ExitYear) return 1;
                if (a.ExitYear && b.ExitYear) return a.ExitYear - b.ExitYear;
                return (a.CountyName || '').localeCompare(b.CountyName || '');
            });
            
            const counties = validCounties.slice(0, 12); // 只显示前12个
            
            if (counties.length === 0) {
                container.innerHTML = '<div class="col-span-3 text-center py-8 opacity-70">暂无符合条件的县</div>';
                return;
            }
            
            container.innerHTML = counties.map(county => `
                <div class="bg-white/10 rounded-xl p-4 card-hover cursor-pointer" onclick="showCountyDetail('${county.CountyCode}')">
                    <div class="font-bold text-xl mb-2">${county.CountyName || county.CountyCode}</div>
                    <div class="text-sm opacity-70 mb-2">${county.Province || '未知'} · ${county.City || '未知'}</div>
                    ${county.ExitYear ? `<div class="text-sm text-green-400"><i class="fas fa-check-circle mr-1"></i>摘帽时间: ${county.ExitYear}</div>` : ''}
                    ${county.Region ? `<div class="text-xs opacity-60 mt-1">${county.Region}</div>` : ''}
                </div>
            `).join('');
        }
    } catch (error) {
        console.error('加载县列表失败:', error);
    }
}

// 显示县详情
async function showCountyDetail(countyCode) {
    try {
        // 获取县基本信息
        const countyRes = await fetch(`${API_BASE}/counties/${countyCode}`);
        const countyData = await countyRes.json();
        
        if (countyData.success) {
            document.getElementById('county-detail-title').textContent = countyData.data.CountyName;
        }
        
        // 获取经济数据
        const economyRes = await fetch(`${API_BASE}/counties/${countyCode}/economy?start_year=2010&end_year=2020`);
        const economyData = await economyRes.json();
        
        if (economyData.success && economyData.data.length > 0) {
            renderEconomyCharts(economyData.data);
        }
        
        // 获取农业数据
        const agriRes = await fetch(`${API_BASE}/counties/${countyCode}/agriculture?start_year=2010&end_year=2020`);
        const agriData = await agriRes.json();
        
        if (agriData.success && agriData.data.length > 0) {
            renderAgricultureCharts(agriData.data, countyCode);
        }
        
        // 跳转到详情页
        fullpage_api.moveTo(4);
    } catch (error) {
        console.error('加载县详情失败:', error);
    }
}

// 渲染经济数据图表（多维度）
function renderEconomyCharts(data) {
    const years = data.map(d => d.Year);
    const latest = data[data.length - 1];
    
    // 1. GDP趋势图
    const gdpChart = echarts.init(document.getElementById('economy-gdp-chart'));
    const gdp = data.map(d => d.GDP ? (d.GDP / 10000).toFixed(2) : null);
    gdpChart.setOption({
        backgroundColor: 'transparent',
        textStyle: { color: '#fff' },
        grid: { left: '15%', right: '10%', top: '15%', bottom: '15%' },
        xAxis: {
            type: 'category',
            data: years,
            axisLine: { lineStyle: { color: 'rgba(255,255,255,0.3)' } }
        },
        yAxis: {
            type: 'value',
            axisLine: { lineStyle: { color: 'rgba(255,255,255,0.3)' } },
            name: '万元',
            nameTextStyle: { color: 'rgba(255,255,255,0.7)' }
        },
        series: [{
            data: gdp,
            type: 'line',
            smooth: true,
            lineStyle: { color: '#6366f1', width: 3 },
            itemStyle: { color: '#6366f1' },
            areaStyle: {
                color: {
                    type: 'linear',
                    x: 0, y: 0, x2: 0, y2: 1,
                    colorStops: [
                        { offset: 0, color: 'rgba(99, 102, 241, 0.3)' },
                        { offset: 1, color: 'rgba(99, 102, 241, 0)' }
                    ]
                }
            }
        }]
    });
    
    // 2. 产业结构饼图
    if (latest && latest.GDP_Primary && latest.GDP_Secondary && latest.GDP_Tertiary) {
        const structureChart = echarts.init(document.getElementById('economy-structure-chart'));
        const total = latest.GDP_Primary + latest.GDP_Secondary + latest.GDP_Tertiary;
        structureChart.setOption({
            backgroundColor: 'transparent',
            textStyle: { color: '#fff' },
            tooltip: { trigger: 'item' },
            legend: {
                orient: 'vertical',
                right: 10,
                top: 'center',
                textStyle: { color: '#fff' }
            },
            series: [{
                type: 'pie',
                radius: ['40%', '70%'],
                data: [
                    { value: latest.GDP_Primary, name: '第一产业', itemStyle: { color: '#34d399' } },
                    { value: latest.GDP_Secondary, name: '第二产业', itemStyle: { color: '#6366f1' } },
                    { value: latest.GDP_Tertiary, name: '第三产业', itemStyle: { color: '#a855f7' } }
                ],
                label: {
                    formatter: '{b}: {c}万元\n({d}%)'
                }
            }]
        });
    }
    
    // 3. 收入水平对比
    const incomeChart = echarts.init(document.getElementById('economy-income-chart'));
    const urbanWage = data.map(d => d.UrbanAvgWage ? (d.UrbanAvgWage / 1000).toFixed(2) : null);
    const ruralIncome = data.map(d => d.RuralDisposableIncome ? (d.RuralDisposableIncome / 1000).toFixed(2) : null);
    incomeChart.setOption({
        backgroundColor: 'transparent',
        textStyle: { color: '#fff' },
        legend: {
            data: ['城镇平均工资', '农村人均可支配收入'],
            textStyle: { color: '#fff' },
            top: 10
        },
        grid: { left: '15%', right: '10%', top: '20%', bottom: '15%' },
        xAxis: {
            type: 'category',
            data: years,
            axisLine: { lineStyle: { color: 'rgba(255,255,255,0.3)' } }
        },
        yAxis: {
            type: 'value',
            axisLine: { lineStyle: { color: 'rgba(255,255,255,0.3)' } },
            name: '千元',
            nameTextStyle: { color: 'rgba(255,255,255,0.7)' }
        },
        series: [
            {
                name: '城镇平均工资',
                data: urbanWage,
                type: 'line',
                smooth: true,
                lineStyle: { color: '#6366f1', width: 3 },
                itemStyle: { color: '#6366f1' }
            },
            {
                name: '农村人均可支配收入',
                data: ruralIncome,
                type: 'line',
                smooth: true,
                lineStyle: { color: '#34d399', width: 3 },
                itemStyle: { color: '#34d399' }
            }
        ]
    });
    
    // 4. 财政收支
    const fiscalChart = echarts.init(document.getElementById('economy-fiscal-chart'));
    const revenue = data.map(d => d.FiscalRevenue ? (d.FiscalRevenue / 10000).toFixed(2) : null);
    const expenditure = data.map(d => d.FiscalExpenditure ? (d.FiscalExpenditure / 10000).toFixed(2) : null);
    fiscalChart.setOption({
        backgroundColor: 'transparent',
        textStyle: { color: '#fff' },
        legend: {
            data: ['财政收入', '财政支出'],
            textStyle: { color: '#fff' },
            top: 10
        },
        grid: { left: '15%', right: '10%', top: '20%', bottom: '15%' },
        xAxis: {
            type: 'category',
            data: years,
            axisLine: { lineStyle: { color: 'rgba(255,255,255,0.3)' } }
        },
        yAxis: {
            type: 'value',
            axisLine: { lineStyle: { color: 'rgba(255,255,255,0.3)' } },
            name: '万元',
            nameTextStyle: { color: 'rgba(255,255,255,0.7)' }
        },
        series: [
            {
                name: '财政收入',
                data: revenue,
                type: 'bar',
                itemStyle: { color: '#34d399' }
            },
            {
                name: '财政支出',
                data: expenditure,
                type: 'bar',
                itemStyle: { color: '#ec4899' }
            }
        ]
    });
}

// 渲染农业数据图表（多维度）
async function renderAgricultureCharts(data, countyCode) {
    const years = data.map(d => d.Year);
    const latest = data[data.length - 1];
    
    // 1. 农业产出趋势
    const outputChart = echarts.init(document.getElementById('agriculture-output-chart'));
    const grain = data.map(d => d.GrainOutput ? (d.GrainOutput / 1000).toFixed(2) : null);
    const meat = data.map(d => d.MeatOutput ? (d.MeatOutput / 1000).toFixed(2) : null);
    const agriValue = data.map(d => d.AgriOutputValue ? (d.AgriOutputValue / 10000).toFixed(2) : null);
    
    outputChart.setOption({
        backgroundColor: 'transparent',
        textStyle: { color: '#fff' },
        legend: {
            data: ['粮食产量(千吨)', '肉类产量(千吨)', '农业总产值(万元)'],
            textStyle: { color: '#fff' },
            top: 10
        },
        grid: { left: '15%', right: '10%', top: '20%', bottom: '15%' },
        xAxis: {
            type: 'category',
            data: years,
            axisLine: { lineStyle: { color: 'rgba(255,255,255,0.3)' } }
        },
        yAxis: [
            {
                type: 'value',
                name: '千吨',
                position: 'left',
                axisLine: { lineStyle: { color: 'rgba(255,255,255,0.3)' } },
                nameTextStyle: { color: 'rgba(255,255,255,0.7)' }
            },
            {
                type: 'value',
                name: '万元',
                position: 'right',
                axisLine: { lineStyle: { color: 'rgba(255,255,255,0.3)' } },
                nameTextStyle: { color: 'rgba(255,255,255,0.7)' }
            }
        ],
        series: [
            {
                name: '粮食产量(千吨)',
                data: grain,
                type: 'bar',
                itemStyle: { color: '#34d399' },
                yAxisIndex: 0
            },
            {
                name: '肉类产量(千吨)',
                data: meat,
                type: 'bar',
                itemStyle: { color: '#ec4899' },
                yAxisIndex: 0
            },
            {
                name: '农业总产值(万元)',
                data: agriValue,
                type: 'line',
                smooth: true,
                lineStyle: { color: '#a855f7', width: 3 },
                itemStyle: { color: '#a855f7' },
                yAxisIndex: 1
            }
        ]
    });
    
    // 2. 农作物结构（饼图）
    try {
        const cropRes = await fetch(`${API_BASE}/counties/${countyCode}/crops?year=${latest.Year || 2020}`);
        const cropData = await cropRes.json();
        
        if (cropData.success && cropData.data.length > 0) {
            const cropChart = echarts.init(document.getElementById('agriculture-crop-chart'));
            const cropTypes = cropData.data
                .sort((a, b) => (b.SownArea || 0) - (a.SownArea || 0))
                .slice(0, 8)
                .map(d => ({
                    value: d.SownArea || 0,
                    name: d.CropType
                }));
            
            cropChart.setOption({
                backgroundColor: 'transparent',
                textStyle: { color: '#fff' },
                tooltip: { trigger: 'item' },
                legend: {
                    orient: 'vertical',
                    right: 10,
                    top: 'center',
                    textStyle: { color: '#fff' },
                    formatter: (name) => {
                        const item = cropTypes.find(c => c.name === name);
                        return item ? `${name}\n${item.value.toFixed(2)}公顷` : name;
                    }
                },
                series: [{
                    type: 'pie',
                    radius: ['40%', '70%'],
                    data: cropTypes,
                    label: {
                        formatter: '{b}\n{d}%'
                    },
                    itemStyle: {
                        borderRadius: 5
                    }
                }]
            });
        }
    } catch (error) {
        console.error('加载农作物数据失败:', error);
    }
    
    // 3. 主要农作物面积趋势
    try {
        const cropAreaRes = await fetch(`${API_BASE}/counties/${countyCode}/crops?year=${latest.Year || 2020}`);
        const cropAreaData = await cropAreaRes.json();
        
        if (cropAreaData.success && cropAreaData.data.length > 0) {
            const areaChart = echarts.init(document.getElementById('agriculture-area-chart'));
            const topCrops = cropAreaData.data
                .sort((a, b) => (b.SownArea || 0) - (a.SownArea || 0))
                .slice(0, 5);
            
            areaChart.setOption({
                backgroundColor: 'transparent',
                textStyle: { color: '#fff' },
                grid: { left: '20%', right: '10%', top: '15%', bottom: '15%' },
                xAxis: {
                    type: 'value',
                    axisLine: { lineStyle: { color: 'rgba(255,255,255,0.3)' } },
                    name: '公顷',
                    nameTextStyle: { color: 'rgba(255,255,255,0.7)' }
                },
                yAxis: {
                    type: 'category',
                    data: topCrops.map(c => c.CropType),
                    axisLine: { lineStyle: { color: 'rgba(255,255,255,0.3)' } }
                },
                series: [{
                    data: topCrops.map(c => c.SownArea || 0),
                    type: 'bar',
                    itemStyle: {
                        color: {
                            type: 'linear',
                            x: 0, y: 0, x2: 1, y2: 0,
                            colorStops: [
                                { offset: 0, color: '#a855f7' },
                                { offset: 1, color: '#ec4899' }
                            ]
                        }
                    }
                }]
            });
        }
    } catch (error) {
        console.error('加载农作物面积数据失败:', error);
    }
}

// 访谈筛选状态
let interviewFilters = {
    county_code: '',
    surveyor_id: '',
    keyword: ''
};

// 打开访谈筛选弹窗
function openInterviewFilter() {
    const modal = document.getElementById('interview-filter-modal');
    if (modal) {
        modal.style.display = 'flex';
        modal.style.pointerEvents = 'auto';
        // 禁用fullpage滚动
        if (typeof fullpage_api !== 'undefined' && fullpage_api.setAllowScrolling) {
            fullpage_api.setAllowScrolling(false);
        }
    }
}

// 关闭访谈筛选弹窗
function closeInterviewFilter() {
    const modal = document.getElementById('interview-filter-modal');
    if (modal) {
        modal.style.display = 'none';
        modal.style.pointerEvents = 'none';
        // 恢复fullpage滚动
        if (typeof fullpage_api !== 'undefined' && fullpage_api.setAllowScrolling) {
            fullpage_api.setAllowScrolling(true);
        }
    }
}

// 应用访谈筛选
function applyInterviewFilter() {
    interviewFilters.county_code = document.getElementById('filter-county-code').value.trim();
    interviewFilters.surveyor_id = document.getElementById('filter-surveyor-id').value.trim();
    interviewFilters.keyword = document.getElementById('filter-keyword').value.trim();
    
    loadInterviews();
    closeInterviewFilter();
}

// 重置访谈筛选
function resetInterviewFilter() {
    document.getElementById('filter-county-code').value = '';
    document.getElementById('filter-surveyor-id').value = '';
    document.getElementById('filter-keyword').value = '';
    interviewFilters = { county_code: '', surveyor_id: '', keyword: '' };
    loadInterviews();
    closeInterviewFilter();
}

// 加载访谈记录
async function loadInterviews(quickKeyword = '') {
    try {
        const params = new URLSearchParams();
        
        // 快速搜索优先，否则使用筛选条件
        if (quickKeyword) {
            params.append('keyword', quickKeyword);
        } else {
            if (interviewFilters.county_code) params.append('county_code', interviewFilters.county_code);
            if (interviewFilters.surveyor_id) params.append('surveyor_id', interviewFilters.surveyor_id);
            if (interviewFilters.keyword) params.append('keyword', interviewFilters.keyword);
        }
        
        params.append('limit', '20');
        
        const response = await fetch(`${API_BASE}/interviews?${params}`);
        const result = await response.json();
        
        if (result.success) {
            const container = document.getElementById('interviews-container');
            
            if (result.data.length === 0) {
                container.innerHTML = '<div class="text-center py-8 opacity-70">暂无访谈记录</div>';
                return;
            }
            
            container.innerHTML = result.data.map(interview => {
                const date = interview.InterviewDate ? new Date(interview.InterviewDate).toLocaleDateString('zh-CN') : '';
                return `
                    <div class="bg-white/10 rounded-xl p-4 card-hover">
                        <div class="flex justify-between items-start mb-2">
                            <div class="flex-1">
                                <div class="font-bold text-lg mb-1">${interview.IntervieweeName || '未知'}</div>
                                <div class="text-sm opacity-70">
                                    ${interview.CountyName || ''}${date ? ' · ' + date : ''}
                                    ${interview.SurveyorName ? ' · 调研员: ' + interview.SurveyorName : ''}
                                </div>
                            </div>
                            ${interview.Quality ? `<div class="text-yellow-400 ml-4"><i class="fas fa-star"></i> ${interview.Quality}</div>` : ''}
                        </div>
                        ${interview.IntervieweeInfo ? `<div class="text-xs opacity-60 mb-2">${interview.IntervieweeInfo}</div>` : ''}
                        <div class="text-sm opacity-80 line-clamp-3">${interview.Content ? interview.Content.substring(0, 300) + (interview.Content.length > 300 ? '...' : '') : ''}</div>
                    </div>
                `;
            }).join('');
        }
    } catch (error) {
        console.error('加载访谈记录失败:', error);
        document.getElementById('interviews-container').innerHTML = '<div class="text-center py-8 text-red-400">加载失败，请检查后端API是否运行</div>';
    }
}

// 对比分析 - 已选择的县
let selectedCountiesForCompare = [];

// 打开县选择器
async function openCountySelector() {
    const modal = document.getElementById('county-selector-modal');
    if (modal) {
        modal.style.display = 'flex';
        document.body.style.overflow = 'hidden'; // 防止背景滚动
        // 加载省份列表
        await loadSelectorProvinces();
        // 加载县列表
        loadCountySelectorList();
        if (typeof fullpage_api !== 'undefined' && fullpage_api.setAllowScrolling) {
            fullpage_api.setAllowScrolling(false);
        }
    }
}

// 加载县选择器的省份列表
async function loadSelectorProvinces() {
    try {
        const response = await fetch(`${API_BASE}/counties`);
        const result = await response.json();

        if (result.success) {
            const provinces = [...new Set(result.data
                .filter(c => c.Province && c.Province !== '未知')
                .map(c => c.Province)
            )].sort();

            const select = document.getElementById('selector-province');
            if (select) {
                const allOption = select.querySelector('option[value=""]');
                select.innerHTML = '';
                if (allOption) select.appendChild(allOption);

                provinces.forEach(province => {
                    const option = document.createElement('option');
                    option.value = province;
                    option.textContent = province;
                    select.appendChild(option);
                });
            }
        }
    } catch (error) {
        console.error('加载省份列表失败:', error);
    }
}

// 关闭县选择器
function closeCountySelector() {
    const modal = document.getElementById('county-selector-modal');
    if (modal) {
        modal.style.display = 'none';
        document.body.style.overflow = ''; // 恢复滚动
        if (typeof fullpage_api !== 'undefined' && fullpage_api.setAllowScrolling) {
            fullpage_api.setAllowScrolling(true);
        }
    }
}

// 加载县选择器列表
async function loadCountySelectorList(filters = {}) {
    try {
        const params = new URLSearchParams();
        if (filters.region) params.append('region', filters.region);
        if (filters.province) params.append('province', filters.province);
        
        const response = await fetch(`${API_BASE}/counties?${params}`);
        const result = await response.json();
        
        if (result.success) {
            const container = document.getElementById('county-selector-list');
            const validCounties = result.data.filter(county => 
                county.CountyName && !county.CountyName.startsWith('县代码')
            );
            
            // 应用搜索过滤
            const searchKeyword = document.getElementById('selector-search')?.value.trim().toLowerCase() || '';
            const filteredCounties = searchKeyword 
                ? validCounties.filter(c => 
                    (c.CountyName || '').toLowerCase().includes(searchKeyword) ||
                    (c.Province || '').toLowerCase().includes(searchKeyword)
                  )
                : validCounties;
            
            container.innerHTML = filteredCounties.map(county => {
                const isSelected = selectedCountiesForCompare.some(sc => sc.CountyCode === county.CountyCode);
                return `
                    <div class="bg-white/10 rounded-lg p-3 cursor-pointer card-hover ${isSelected ? 'ring-2 ring-indigo-500' : ''}" 
                         onclick="toggleCountySelection('${county.CountyCode}', '${county.CountyName}')">
                        <div class="flex items-center justify-between">
                            <div class="flex-1">
                                <div class="font-semibold">${county.CountyName}</div>
                                <div class="text-xs opacity-70">${county.Province || ''} · ${county.City || ''}</div>
                            </div>
                            ${isSelected ? '<i class="fas fa-check-circle text-indigo-400 ml-2"></i>' : ''}
                        </div>
                    </div>
                `;
            }).join('');
        }
    } catch (error) {
        console.error('加载县列表失败:', error);
    }
}

// 切换县选择
function toggleCountySelection(countyCode, countyName) {
    const index = selectedCountiesForCompare.findIndex(c => c.CountyCode === countyCode);
    if (index >= 0) {
        selectedCountiesForCompare.splice(index, 1);
    } else {
        if (selectedCountiesForCompare.length >= 5) {
            alert('最多选择5个县进行对比');
            return;
        }
        selectedCountiesForCompare.push({ CountyCode: countyCode, CountyName: countyName });
    }
    loadCountySelectorList();
    updateSelectedCountiesDisplay();
}

// 更新已选择县的显示
function updateSelectedCountiesDisplay() {
    const container = document.getElementById('selected-counties');
    if (selectedCountiesForCompare.length === 0) {
        container.innerHTML = '<div class="text-sm opacity-70">未选择任何县</div>';
    } else {
        container.innerHTML = selectedCountiesForCompare.map(county => `
            <div class="bg-indigo-600/30 border border-indigo-500 rounded-lg px-4 py-2 flex items-center gap-2">
                <span>${county.CountyName}</span>
                <button onclick="removeSelectedCounty('${county.CountyCode}')" class="text-white/70 hover:text-white">
                    <i class="fas fa-times"></i>
                </button>
            </div>
        `).join('');
    }
}

// 移除已选择的县
function removeSelectedCounty(countyCode) {
    selectedCountiesForCompare = selectedCountiesForCompare.filter(c => c.CountyCode !== countyCode);
    updateSelectedCountiesDisplay();
}

// 应用县选择
function applyCountySelection() {
    closeCountySelector();
    updateSelectedCountiesDisplay();
    // 如果已选择县，自动加载对比数据
    if (selectedCountiesForCompare.length >= 2) {
        loadCompareData();
    }
}

// 加载对比数据
async function loadCompareData() {
    let countyCodes = [];
    
    // 优先使用已选择的县
    if (selectedCountiesForCompare.length > 0) {
        countyCodes = selectedCountiesForCompare.map(c => c.CountyCode);
    } else {
        // 否则使用输入框的值
        const input = document.getElementById('compare-input').value;
        countyCodes = input.split(',').map(c => c.trim()).filter(c => c);
    }
    
    if (countyCodes.length < 2) {
        alert('请至少选择或输入2个县代码');
        return;
    }
    
    if (countyCodes.length > 5) {
        alert('最多对比5个县');
        return;
    }
    
    const metric = document.getElementById('compare-metric').value;
    const chartType = document.getElementById('compare-chart-type').value;
    const metricMap = {
        'GDP': 'GDP',
        'PerCapitaGDP': 'PerCapitaGDP',
        'RuralDisposableIncome': 'RuralDisposableIncome',
        'AgriOutputValue': 'AgriOutputValue',
        'FiscalRevenue': 'FiscalRevenue',
        'FiscalExpenditure': 'FiscalExpenditure',
        'GrainOutput': 'GrainOutput',
        'MeatOutput': 'MeatOutput',
        'IndustrialOutput': 'IndustrialOutput',
        'RetailSales': 'RetailSales'
    };
    
    try {
        const params = new URLSearchParams();
        countyCodes.forEach(code => params.append('county_code', code));
        params.append('metric', metricMap[metric] || 'GDP');
        params.append('start_year', '2010');
        params.append('end_year', '2020');
        
        const response = await fetch(`${API_BASE}/compare/trend?${params}`);
        const result = await response.json();
        
        if (result.success) {
            renderCompareChart(result.data, metric, chartType);
        }
    } catch (error) {
        console.error('加载对比数据失败:', error);
    }
}

// 渲染对比图表
function renderCompareChart(data, metric = 'GDP', chartType = 'line') {
    const chart = echarts.init(document.getElementById('compare-chart'));
    
    // 按县分组数据
    const countyMap = {};
    data.forEach(d => {
        if (!countyMap[d.CountyCode]) {
            countyMap[d.CountyCode] = {
                name: d.CountyName,
                data: []
            };
        }
        const value = d[metric] || d.GDP || 0;
        countyMap[d.CountyCode].data.push([d.Year, value]);
    });
    
    const years = [...new Set(data.map(d => d.Year))].sort();
    const colors = ['#6366f1', '#a855f7', '#ec4899', '#34d399', '#f59e0b'];
    
    // 计算除数
    const divisorMap = {
        'AgriOutputValue': 10000,
        'GDP': 10000,
        'FiscalRevenue': 10000,
        'FiscalExpenditure': 10000,
        'IndustrialOutput': 10000,
        'RetailSales': 10000,
        'GrainOutput': 1000,
        'MeatOutput': 1000
    };
    const divisor = divisorMap[metric] || 1;
    
    const series = Object.values(countyMap).map((county, idx) => {
        const seriesData = years.map(year => {
            const point = county.data.find(d => d[0] === year);
            return point ? (point[1] / divisor) : null;
        });
        
        const baseConfig = {
            name: county.name,
            data: seriesData,
            itemStyle: { color: colors[idx % colors.length] }
        };
        
        if (chartType === 'line') {
            return {
                ...baseConfig,
                type: 'line',
                smooth: true,
                lineStyle: { width: 3 },
                areaStyle: {
                    color: {
                        type: 'linear',
                        x: 0, y: 0, x2: 0, y2: 1,
                        colorStops: [
                            { offset: 0, color: colors[idx % colors.length] + '80' },
                            { offset: 1, color: colors[idx % colors.length] + '00' }
                        ]
                    }
                }
            };
        } else if (chartType === 'bar') {
            return {
                ...baseConfig,
                type: 'bar',
                barWidth: '60%'
            };
        } else if (chartType === 'area') {
            return {
                ...baseConfig,
                type: 'line',
                smooth: true,
                lineStyle: { width: 2 },
                areaStyle: {
                    color: colors[idx % colors.length] + '40'
                }
            };
        }
    });
    
    const unitMap = {
        'GDP': '万元',
        'PerCapitaGDP': '元',
        'RuralDisposableIncome': '元',
        'AgriOutputValue': '万元',
        'FiscalRevenue': '万元',
        'FiscalExpenditure': '万元',
        'GrainOutput': '千吨',
        'MeatOutput': '千吨',
        'IndustrialOutput': '万元',
        'RetailSales': '万元'
    };
    
    const option = {
        backgroundColor: 'transparent',
        textStyle: { color: '#fff' },
        title: {
            text: unitMap[metric] || '万元',
            left: 'center',
            top: 10,
            textStyle: { color: '#fff', fontSize: 14 }
        },
        legend: {
            data: Object.values(countyMap).map(c => c.name),
            textStyle: { color: '#fff' },
            top: 35
        },
        grid: { left: '12%', right: '10%', top: '25%', bottom: '15%' },
        xAxis: {
            type: 'category',
            data: years,
            axisLine: { lineStyle: { color: 'rgba(255,255,255,0.3)' } }
        },
        yAxis: {
            type: 'value',
            axisLine: { lineStyle: { color: 'rgba(255,255,255,0.3)' } },
            name: unitMap[metric] || '万元',
            nameTextStyle: { color: 'rgba(255,255,255,0.7)' }
        },
        series: series
    };
    
    chart.setOption(option);
    
    // 渲染饼图（显示最新年份的占比）
    renderComparePieChart(data, metric, years[years.length - 1] || 2020);
}

// 渲染对比饼图（显示最新年份各县的占比）
function renderComparePieChart(data, metric, year) {
    const pieChart = echarts.init(document.getElementById('compare-pie-chart'));
    
    // 获取指定年份的数据
    const yearData = data.filter(d => d.Year === year);
    if (yearData.length === 0) {
        pieChart.setOption({
            backgroundColor: 'transparent',
            textStyle: { color: '#fff' },
            title: {
                text: '暂无数据',
                left: 'center',
                top: 'center',
                textStyle: { color: '#fff' }
            }
        });
        return;
    }
    
    const divisorMap = {
        'AgriOutputValue': 10000,
        'GDP': 10000,
        'FiscalRevenue': 10000,
        'FiscalExpenditure': 10000,
        'IndustrialOutput': 10000,
        'RetailSales': 10000,
        'GrainOutput': 1000,
        'MeatOutput': 1000
    };
    const divisor = divisorMap[metric] || 1;
    
    const pieData = yearData.map((d, idx) => {
        const colors = ['#6366f1', '#a855f7', '#ec4899', '#34d399', '#f59e0b'];
        return {
            value: (d[metric] || 0) / divisor,
            name: d.CountyName,
            itemStyle: { color: colors[idx % colors.length] }
        };
    });
    
    const unitMap = {
        'GDP': '万元',
        'PerCapitaGDP': '元',
        'RuralDisposableIncome': '元',
        'AgriOutputValue': '万元',
        'FiscalRevenue': '万元',
        'FiscalExpenditure': '万元',
        'GrainOutput': '千吨',
        'MeatOutput': '千吨',
        'IndustrialOutput': '万元',
        'RetailSales': '万元'
    };
    
    pieChart.setOption({
        backgroundColor: 'transparent',
        textStyle: { color: '#fff' },
        title: {
            text: `${year}年占比`,
            left: 'center',
            top: 10,
            textStyle: { color: '#fff', fontSize: 14 }
        },
        tooltip: {
            trigger: 'item',
            formatter: '{b}: {c} ' + (unitMap[metric] || '万元') + ' ({d}%)'
        },
        legend: {
            orient: 'vertical',
            right: 10,
            top: 'center',
            textStyle: { color: '#fff' }
        },
        series: [{
            type: 'pie',
            radius: ['40%', '70%'],
            center: ['40%', '50%'],
            data: pieData,
            label: {
                formatter: '{b}\n{d}%'
            },
            emphasis: {
                itemStyle: {
                    shadowBlur: 10,
                    shadowOffsetX: 0,
                    shadowColor: 'rgba(0, 0, 0, 0.5)'
                }
            }
        }]
    });
}

// 事件监听
document.getElementById('region-filter')?.addEventListener('change', (e) => {
    const filters = {
        region: e.target.value,
        province: document.getElementById('province-filter')?.value || ''
    };
    loadCounties(filters);
});

document.getElementById('province-filter')?.addEventListener('change', (e) => {
    const filters = {
        region: document.getElementById('region-filter')?.value || '',
        province: e.target.value
    };
    loadCounties(filters);
});

document.getElementById('search-input')?.addEventListener('input', (e) => {
    const keyword = e.target.value.trim().toLowerCase();
    if (keyword) {
        // 实时搜索县名
        const cards = document.querySelectorAll('#counties-container > div');
        cards.forEach(card => {
            const countyName = card.querySelector('.font-bold')?.textContent?.toLowerCase() || '';
            const province = card.querySelector('.text-sm')?.textContent?.toLowerCase() || '';
            if (countyName.includes(keyword) || province.includes(keyword)) {
                card.style.display = '';
            } else {
                card.style.display = 'none';
            }
        });
    } else {
        // 显示所有卡片
        const cards = document.querySelectorAll('#counties-container > div');
        cards.forEach(card => card.style.display = '');
    }
});

document.getElementById('interview-search')?.addEventListener('input', (e) => {
    const keyword = e.target.value.trim();
    if (keyword) {
        loadInterviews(keyword);
    } else {
        // 如果快速搜索框为空，使用筛选条件
        loadInterviews();
    }
});

// 点击弹窗外部关闭
document.addEventListener('DOMContentLoaded', function() {
    const modal = document.getElementById('interview-filter-modal');
    if (modal) {
        modal.addEventListener('click', (e) => {
            // 点击背景（不是内容区域）时关闭
            if (e.target.id === 'interview-filter-modal' || e.target.classList.contains('bg-black/80')) {
                closeInterviewFilter();
            }
        });
    }
});

// 初始化加载访谈
setTimeout(() => {
    loadInterviews();
}, 1000);

// 县选择器事件监听
document.getElementById('selector-region')?.addEventListener('change', (e) => {
    const filters = {
        region: e.target.value,
        province: document.getElementById('selector-province')?.value || ''
    };
    loadCountySelectorList(filters);
});

document.getElementById('selector-province')?.addEventListener('change', (e) => {
    const filters = {
        region: document.getElementById('selector-region')?.value || '',
        province: e.target.value
    };
    loadCountySelectorList(filters);
});

document.getElementById('selector-search')?.addEventListener('input', (e) => {
    loadCountySelectorList();
});

// 点击县选择器外部关闭
document.addEventListener('DOMContentLoaded', function() {
    const modal = document.getElementById('county-selector-modal');
    if (modal) {
        modal.addEventListener('click', (e) => {
            if (e.target.id === 'county-selector-modal' || e.target.classList.contains('bg-black/80')) {
                closeCountySelector();
            }
        });
    }
    
    // 对比指标和图表类型变化时自动更新图表
    const compareMetricSelect = document.getElementById('compare-metric');
    const compareChartTypeSelect = document.getElementById('compare-chart-type');
    if (compareMetricSelect) {
        compareMetricSelect.addEventListener('change', function() {
            // 如果已经有选中的县，自动重新加载对比数据
            if (selectedCountiesForCompare.length >= 2) {
                loadCompareData();
            }
        });
    }
    if (compareChartTypeSelect) {
        compareChartTypeSelect.addEventListener('change', function() {
            // 如果已经有选中的县，自动重新加载对比数据
            if (selectedCountiesForCompare.length >= 2) {
                loadCompareData();
            }
        });
    }
    
    // 初始化已选择县的显示
    updateSelectedCountiesDisplay();
});

