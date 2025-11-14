// API基础URL
const API_BASE = 'http://localhost:5001/api';

// 初始化FullPage.js
let fullpage_api;
document.addEventListener('DOMContentLoaded', function() {
    fullpage_api = new fullpage('#fullpage', {
        licenseKey: 'gplv3-license',
        navigation: true,
        navigationPosition: 'right',
        scrollingSpeed: 700,
        parallax: true,
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
            
            // 按摘帽时间排序，有摘帽时间的优先，然后按县名排序
            validCounties.sort((a, b) => {
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
            renderEconomyChart(economyData.data);
        }
        
        // 获取农业数据
        const agriRes = await fetch(`${API_BASE}/counties/${countyCode}/agriculture?start_year=2010&end_year=2020`);
        const agriData = await agriRes.json();
        
        if (agriData.success && agriData.data.length > 0) {
            renderAgricultureChart(agriData.data);
        }
        
        // 跳转到详情页
        fullpage_api.moveTo(4);
    } catch (error) {
        console.error('加载县详情失败:', error);
    }
}

// 渲染经济数据图表
function renderEconomyChart(data) {
    const chart = echarts.init(document.getElementById('economy-chart'));
    
    const years = data.map(d => d.Year);
    const gdp = data.map(d => d.GDP ? (d.GDP / 10000).toFixed(2) : 0);
    
    const option = {
        backgroundColor: 'transparent',
        textStyle: { color: '#fff' },
        grid: { left: '10%', right: '10%', top: '15%', bottom: '15%' },
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
    };
    
    chart.setOption(option);
}

// 渲染农业数据图表
function renderAgricultureChart(data) {
    const chart = echarts.init(document.getElementById('agriculture-chart'));
    
    const years = data.map(d => d.Year);
    const grain = data.map(d => d.GrainOutput ? (d.GrainOutput / 1000).toFixed(2) : 0);
    
    const option = {
        backgroundColor: 'transparent',
        textStyle: { color: '#fff' },
        grid: { left: '10%', right: '10%', top: '15%', bottom: '15%' },
        xAxis: {
            type: 'category',
            data: years,
            axisLine: { lineStyle: { color: 'rgba(255,255,255,0.3)' } }
        },
        yAxis: {
            type: 'value',
            axisLine: { lineStyle: { color: 'rgba(255,255,255,0.3)' } },
            name: '千吨',
            nameTextStyle: { color: 'rgba(255,255,255,0.7)' }
        },
        series: [{
            data: grain,
            type: 'bar',
            itemStyle: {
                color: {
                    type: 'linear',
                    x: 0, y: 0, x2: 0, y2: 1,
                    colorStops: [
                        { offset: 0, color: '#a855f7' },
                        { offset: 1, color: '#ec4899' }
                    ]
                }
            }
        }]
    };
    
    chart.setOption(option);
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

// 加载对比数据
async function loadCompareData() {
    const input = document.getElementById('compare-input').value;
    const countyCodes = input.split(',').map(c => c.trim()).filter(c => c);
    
    if (countyCodes.length < 2) {
        alert('请至少输入2个县代码');
        return;
    }
    
    try {
        const params = new URLSearchParams();
        countyCodes.forEach(code => params.append('county_code', code));
        params.append('metric', 'GDP');
        params.append('start_year', '2010');
        params.append('end_year', '2020');
        
        const response = await fetch(`${API_BASE}/compare/trend?${params}`);
        const result = await response.json();
        
        if (result.success) {
            renderCompareChart(result.data);
        }
    } catch (error) {
        console.error('加载对比数据失败:', error);
    }
}

// 渲染对比图表
function renderCompareChart(data) {
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
        countyMap[d.CountyCode].data.push([d.Year, d.GDP]);
    });
    
    const years = [...new Set(data.map(d => d.Year))].sort();
    const series = Object.values(countyMap).map((county, idx) => ({
        name: county.name,
        type: 'line',
        smooth: true,
        data: years.map(year => {
            const point = county.data.find(d => d[0] === year);
            return point ? (point[1] / 10000).toFixed(2) : null;
        }),
        lineStyle: { width: 3 },
        itemStyle: { color: ['#6366f1', '#a855f7', '#ec4899', '#34d399'][idx % 4] }
    }));
    
    const option = {
        backgroundColor: 'transparent',
        textStyle: { color: '#fff' },
        legend: {
            data: Object.values(countyMap).map(c => c.name),
            textStyle: { color: '#fff' },
            top: 10
        },
        grid: { left: '10%', right: '10%', top: '20%', bottom: '15%' },
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
        series: series
    };
    
    chart.setOption(option);
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

