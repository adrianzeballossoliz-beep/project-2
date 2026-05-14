// Global chart instances to destroy them before re-rendering
const charts = {};

// Color Palette
const COLORS = [
    'rgba(212, 175, 55, 0.8)', // Gold
    'rgba(58, 134, 255, 0.8)',  // Blue
    'rgba(0, 242, 96, 0.8)',   // Emerald
    'rgba(131, 56, 236, 0.8)', // Purple
    'rgba(255, 0, 110, 0.8)'   // Pink
];

const BORDER_COLORS = [
    '#D4AF37', '#3A86FF', '#00F260', '#8338EC', '#FF006E'
];

Chart.defaults.color = '#A0A5B1';
Chart.defaults.font.family = "'Plus Jakarta Sans', sans-serif";

$(document).ready(function() {
    // Menu Toggle
    $("#menu-toggle").click(function(e) {
        e.preventDefault();
        $("#wrapper").toggleClass("toggled");
    });

    // Initialize DataTable in Spanish
    const dataTable = $('#customersTable').DataTable({
        pageLength: 5,
        lengthMenu: [5, 10, 25, 50],
        language: {
            url: "//cdn.datatables.net/plug-ins/1.13.6/i18n/es-ES.json"
        },
        columns: [
            { data: 'customer_name' },
            { data: 'segment' },
            { data: 'region' },
            { data: 'total_orders', render: $.fn.dataTable.render.number(',', '.', 0) },
            { data: 'total_sales', render: $.fn.dataTable.render.number(',', '.', 2, '$') },
            { data: 'total_profit', render: $.fn.dataTable.render.number(',', '.', 2, '$') },
            { data: 'avg_ticket', render: $.fn.dataTable.render.number(',', '.', 2, '$') }
        ]
    });

    // Load Filters
    fetch('/api/filters')
        .then(res => res.json())
        .then(data => {
            data.segments.forEach(s => $('#segmentFilter').append(new Option(s, s)));
            data.regions.forEach(r => $('#regionFilter').append(new Option(r, r)));
            data.years.forEach(y => $('#yearFilter').append(new Option(y, y)));
            // data.categories processing left out if model has no Category string right there, or handle it
            if(data.categories) {
                data.categories.forEach(c => $('#categoryFilter').append(new Option(c, c)));
            }
            loadDashboardData();
        });

    // Filter Change Event
    $('.filter-select').on('change', function() {
        loadDashboardData();
    });

    // Reset Filters Event
    $('#resetFiltersBtn').on('click', function() {
        $('.filter-select').val('All');
        loadDashboardData();
    });

    function loadDashboardData() {
        const segment = $('#segmentFilter').val();
        const region = $('#regionFilter').val();
        const year = $('#yearFilter').val();
        // Option to pass category if API supports it later

        // Construct query parameters
        const params = new URLSearchParams();
        if (segment !== 'All') params.append('segment', segment);
        if (region !== 'All') params.append('region', region);
        if (year !== 'All') params.append('year', year);

        fetch(`/api/data?${params.toString()}`)
            .then(res => res.json())
            .then(data => {
                updateKPIs(data.kpis);
                renderSalesBySegment(data.ventas_por_segmento);
                renderTopCustomers(data.top_10_clientes);
                renderCustomersByRegion(data.clientes_por_region);
                renderExpectedLTV(data.ticket_promedio_segmento); // Map this to Ticket Promedio por Segmento
                
                // Update DataTable
                dataTable.clear();
                dataTable.rows.add(data.ranking_clientes);
                dataTable.draw();
            })
            .catch(err => {
                console.error("Error cargando dashboard: ", err);
            });
    }

    // Number format helper
    const formatCurrency = (val) => new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(val);
    const formatNumber = (val) => new Intl.NumberFormat('en-US').format(val);

    function updateKPIs(kpis) {
        // Animate numbers up
        $({ counter: 0 }).animate({ counter: kpis.total_customers }, {
            duration: 1000,
            easing: 'swing',
            step: function() { $('#kpi-total-customers').text(formatNumber(Math.ceil(this.counter))); },
            complete: function() { $('#kpi-total-customers').text(formatNumber(kpis.total_customers)); }
        });
        
        $({ counter: 0 }).animate({ counter: kpis.active_customers }, {
            duration: 1000,
            step: function() { $('#kpi-active-customers').text(formatNumber(Math.ceil(this.counter))); },
            complete: function() { $('#kpi-active-customers').text(formatNumber(kpis.active_customers)); }
        });

        $({ counter: 0 }).animate({ counter: kpis.avg_ticket }, {
            duration: 1000,
            step: function() { $('#kpi-avg-ticket').text(formatCurrency(this.counter)); },
            complete: function() { $('#kpi-avg-ticket').text(formatCurrency(kpis.avg_ticket)); }
        });

        $({ counter: 0 }).animate({ counter: kpis.avg_sales_per_customer }, {
            duration: 1000,
            step: function() { $('#kpi-avg-sales').text(formatCurrency(this.counter)); },
            complete: function() { $('#kpi-avg-sales').text(formatCurrency(kpis.avg_sales_per_customer)); }
        });
    }

    function createChart(chartId, type, data, options) {
        const ctx = document.getElementById(chartId).getContext('2d');
        if (charts[chartId]) charts[chartId].destroy();
        charts[chartId] = new Chart(ctx, { type, data, options });
    }

    function renderSalesBySegment(data) {
        const labels = data.map(d => d.segment);
        const values = data.map(d => d.sales);
        
        createChart('chartSalesSegment', 'doughnut', {
            labels,
            datasets: [{
                data: values,
                backgroundColor: COLORS,
                borderColor: 'rgba(9, 10, 16, 1)',
                borderWidth: 2,
                hoverOffset: 10
            }]
        }, {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { position: 'bottom', labels: { color: '#fff', font: {family: "'Plus Jakarta Sans'"} } },
                tooltip: { callbacks: { label: function(context) { return formatCurrency(context.raw); } }}
            },
            cutout: '70%'
        });
    }

    function renderTopCustomers(data) {
        const labels = data.map(d => d.customer);
        const values = data.map(d => d.sales);

        createChart('chartTopCustomers', 'bar', {
            labels,
            datasets: [{
                label: 'Ventas USD',
                data: values,
                backgroundColor: 'rgba(212, 175, 55, 0.4)',
                borderColor: '#D4AF37',
                borderWidth: 1,
                borderRadius: 4
            }]
        }, {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: { grid: { color: 'rgba(255,255,255,0.05)' }, ticks: { callback: function(value) { return '$' + value; }, color: '#A0A5B1' } },
                x: { grid: { display: false }, ticks: { color: '#A0A5B1'} }
            },
            plugins: { legend: { display: false } }
        });
    }

    function renderCustomersByRegion(data) {
        const labels = data.map(d => d.region);
        const values = data.map(d => d.customers);
        
        createChart('chartCustomersRegion', 'polarArea', {
            labels,
            datasets: [{
                data: values,
                backgroundColor: [
                    'rgba(58, 134, 255, 0.5)',
                    'rgba(0, 242, 96, 0.5)',
                    'rgba(212, 175, 55, 0.5)',
                    'rgba(131, 56, 236, 0.5)'
                ],
                borderColor: '#090A10',
                borderWidth: 2
            }]
        }, {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { position: 'bottom', labels: { color: '#fff' } }
            },
            scales: {
                r: { ticks: { backdropColor: 'transparent', display: false }, grid: { color: 'rgba(255,255,255,0.05)' } }
            }
        });
    }

    function renderExpectedLTV(data) {
        if (!data) return;
        const labels = data.map(d => d.segment);
        const values = data.map(d => d.avg_ticket); // API sends avg_ticket
        
        let gradientCtx = document.getElementById('chartAvgTicketSegment').getContext('2d');
        let gradient = gradientCtx.createLinearGradient(0, 0, 0, 400);
        gradient.addColorStop(0, 'rgba(0, 242, 96, 0.3)');
        gradient.addColorStop(1, 'rgba(0, 242, 96, 0.0)');

        createChart('chartAvgTicketSegment', 'line', {
            labels,
            datasets: [{
                label: 'Ticket Promedio',
                data: values,
                borderColor: '#00F260',
                backgroundColor: gradient,
                borderWidth: 3,
                fill: true,
                tension: 0.4,
                pointBackgroundColor: '#00F260',
                pointBorderColor: '#090A10',
                pointBorderWidth: 2,
                pointRadius: 5,
                pointHoverRadius: 8
            }]
        }, {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: { grid: { color: 'rgba(255,255,255,0.05)' }, ticks: { callback: function(value) { return '$' + value; } } },
                x: { grid: { display: false } }
            },
            plugins: { legend: { display: false } }
        });
    }

});
