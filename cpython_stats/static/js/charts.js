function create_table(name, endpoint) {
    var ctx = document.getElementById(name);
    var myChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                <!-- fill: false, -->
                label: 'Coredevs + non core devs',
                data: [],
                backgroundColor: [
                    'rgba(54, 162, 235, 0.2)',
                    'rgba(255, 206, 86, 0.2)',
                    'rgba(255, 99, 132, 0.2)',
                    'rgba(75, 192, 192, 0.2)',
                    'rgba(153, 102, 255, 0.2)',
                    'rgba(255, 159, 64, 0.2)'
                ],
                borderColor: [
                    'rgba(255,99,132,1)',
                    'rgba(54, 162, 235, 1)',
                    'rgba(255, 206, 86, 1)',
                    'rgba(75, 192, 192, 1)',
                    'rgba(153, 102, 255, 1)',
                    'rgba(255, 159, 64, 1)'
                ],
                borderWidth: 1
            }]
        },
        options: {
            <!-- elements: { point: { radius: 0 } }, -->
            elements: {point: {radius: 0}},
            responsive: true,
            title: {
                display: true,
                text: 'Open Pull Request over time'
            },
            tooltips: {
                enabled: false,
                mode: 'index',
                intersect: false,
            },
            hover: {
                mode: 'nearest',
                intersect: true
            },
            scales: {
                xAxes: [{
                    ticks: {
                        autoSkip: true,
                        maxTicksLimit: 20
                    },
                    type: "time",
                    display: true,
                    scaleLabel: {
                        display: true,
                        labelString: 'Date'
                    }
                }],
                yAxes: [{
                    display: true,
                    scaleLabel: {
                        display: true,
                        labelString: '# of PRs'
                    }
                }]
            }
        }
    });

    $.get(endpoint, function (data) {
        data.forEach(function (item) {
            myChart.data.labels.push(item.date);
            myChart.data.datasets[0].data.push(item.n);
        });
        myChart.update();
    });
}

create_table("merge_over_time", "/get_merge_times");
create_table("canvas", "/get_prs");
