var ctx = document.getElementById("canvas");
var myChart = new Chart(ctx, {
    type: 'line',
    data: {
        labels: [],
        datasets: [{
            <!-- fill: false, -->
            label: 'INBOX',
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
        elements: { point: { radius: 0 } },
        responsive: true,
        title: {
            display: true,
            text: 'Inbox size vs time'
        },
        tooltips: {
            enabled: false,
            mode: 'index',
            intersect: false,
        },
        <!-- hover: { -->
        <!--     mode: 'nearest', -->
        <!--     intersect: true -->
        <!-- }, -->
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
                    labelString: '# of mails'
                }
            }]
        }
    }
 });

$.get( "/get_prs", function( data ) {
data.forEach(function(item){
  myChart.data.labels.push(item.date);
  myChart.data.datasets[0].data.push(item.n);
});
myChart.update();
});
