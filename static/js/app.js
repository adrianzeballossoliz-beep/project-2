$(document).ready(function() {

    // Toggle Sidebar
    $("#menu-toggle").click(function(e) {
        e.preventDefault();
        $("#wrapper").toggleClass("toggled");
    });

    // Chart instances
    let chartSalesSegment, chartTopCustomers, chartCustomersRegion, chartAvgTicketSegment;
    // DataTable instance
    let customersTable;

    // Initialize formatting and common tools
    const formatCurrency = (val) => new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(val);
    const formatNumber = (val) => new Intl.NumberFormat('en-US').format(val);

    // Dark theme default for charts
    Chart.defaults.color = '#a0a5b1';
    Chart.defaults.borderColor = 'rgba(255, 255, 255, 0.05)';
    
    const colors = [
        'rgba(78, 115, 223, 0.8)',
        'rgba(28, 200, 138, 0.8)',
        'rgba(54, 185, 204, 0.8)',
        'rgba(246, 194, 62, 0.8)',
        'rgba(231, 74, 59, 0.8)',
        'rgba(133, 135, 150, 0.8)'
    ];

    // Load Filters
    function loadFilters() {
        fetch('/api/filters')
            .then(res => res.json())
            .then(data => {
                data.segments.forEach(seg => $('#segmentFilter').append(new Option(seg, seg)));
                data.regions.forEach(reg => $('#regionFilter').append(new Option(reg, reg)));
                data.years.forEach(year => $('#yearFilter').append(new Option(year, year)));
                data.categories.forEach(cat => $('#categoryFilter').append(new Option(cat, cat)));
                
                // Once filters are loaded, fetch initial data
                fetchData();
            });
    }

    // Event listeners for filters
    $('.filter-select').on('change', function() {
        fetchData();
    });

    // Fetch Dashboard Data
    function fetchData() {
        const params = new URLSearchParams({
            segment: $('#segmentFilter').val(),
            region: $('#regionFilter').val(),
            year: $('#yearFilter').val(),
            category: $('#categoryFilter').val()
        });

        // Show loading state (optional polish step)

        fetch(`/api/data?${params.toString()}`)
            .then(res => res.json())
            .then(data => {
                updateKPIs(data.kpis);
                updateCharts(data);
                updateDataTable(data.ranking_clientes);
            })
            .catch(err => console.error("Error fetching data:", err));
    }

    function updateKPIs(kpis) {
        animateValue("kpi-total-customers", kpis.total_customers, formatNumber);
        animateValue("kpi-active-customers", kpis.active_customers, formatNumber);
        animateValue("kpi-avg-ticket", kpis.avg_ticket, formatCurrency);
        animateValue("kpi-avg-sales", kpis.avg_sales_per_customer, formatCurrency);
    }

    function animateValue(id, end, formatter) {
        // Simple fast update
        document.getElementById(id).textContent = formatter(end);
    }

    function updateCharts(data) {
        // 1. Sales by Segment
        if(chartSalesSegment) chartSalesSegment.destroy();
        chartSalesSegment = new Chart(document.getElementById('chartSalesSegment'), {
            type: 'doughnut',
            data: {
                labels: data.ventas_por_segmento.map(d => d.segment),
                datasets: [{
                    data: data.ventas_por_segmento.map(d => d.sales),
                    backgroundColor: colors,
                    borderWidth: 0
                }]
            },
            options: {
                responsive: true, maintainAspectRatio: false,
                plugins: { legend: { position: 'bottom' } }
            }
        });

        // 2. Top 10 Customers
        if(chartTopCustomers) chartTopCustomers.destroy();
        chartTopCustomers = new Chart(document.getElementById('chartTopCustomers'), {
            type: 'bar',
            data: {
                labels: data.top_10_clientes.map(d => d.customer),
                datasets: [{
                    label: 'Sales ($)',
                    data: data.top_10_clientes.map(d => d.sales),
                    backgroundColor: colors[0],
                    borderRadius: 4
                }]
            },
            options: {
                responsive: true, maintainAspectRatio: false,
                indexAxis: 'y', // Horizontal bar
                plugins: { legend: { display: false } }
            }
        });

        // 3. Customers by Region
        if(chartCustomersRegion) chartCustomersRegion.destroy();
        chartCustomersRegion = new Chart(document.getElementById('chartCustomersRegion'), {
            type: 'pie',
            data: {
                labels: data.clientes_por_region.map(d => d.region),
                datasets: [{
                    data: data.clientes_por_region.map(d => d.customers),
                    backgroundColor: colors,
                    borderWidth: 0
                }]
            },
            options: {
                responsive: true, maintainAspectRatio: false,
                plugins: { legend: { position: 'bottom' } }
            }
        });

        // 4. Avg Ticket by Segment
        if(chartAvgTicketSegment) chartAvgTicketSegment.destroy();
        chartAvgTicketSegment = new Chart(document.getElementById('chartAvgTicketSegment'), {
            type: 'bar',
            data: {
                labels: data.ticket_promedio_segmento.map(d => d.segment),
                datasets: [{
                    label: 'Average Ticket ($)',
                    data: data.ticket_promedio_segmento.map(d => d.avg_ticket),
                    backgroundColor: colors[1],
                    borderRadius: 4
                }]
            },
            options: {
                responsive: true, maintainAspectRatio: false,
                plugins: { legend: { display: false } }
            }
        });
    }

    function updateDataTable(rankingData) {
        if(customersTable) {
            customersTable.clear().rows.add(rankingData).draw();
        } else {
            customersTable = $('#customersTable').DataTable({
                data: rankingData,
                columns: [
                    { data: 'customer_name' },
                    { data: 'segment' },
                    { data: 'region' },
                    { data: 'total_orders' },
                    { data: 'total_sales', render: $.fn.dataTable.render.number(',', '.', 2, '$') },
                    { data: 'total_profit', render: $.fn.dataTable.render.number(',', '.', 2, '$') },
                    { data: 'avg_ticket', render: $.fn.dataTable.render.number(',', '.', 2, '$') }
                ],
                order: [[4, 'desc']], // Sort by sales desc
                pageLength: 10,
                language: { search: "", searchPlaceholder: "Search records..." }
            });
        }
    }

    // Init
    loadFilters();
});
