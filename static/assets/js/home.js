
// grafico home

let el = document.getElementById("graph_chart")

let options = {
    chart: {
        type: 'line',
        width: 100+'%',
        height: 450,
        
    },
    responsive: [{
        breakpoint: 990,
        options: {
            chart: {
            height: 350,
            },
            legend: {
            position: 'bottom'
            }
        }
    }],
    series:[
        {
            name: 'No TPA',
            data: [22,18,32,56,63,26,42]
        }
        ,{
            name: 'Categorias',
            data: [12, 35,76,45,23,45,28]
        },
        {
            name: 'Em Mão',
            data: [2,8,10,30,83,66,0]
        }
    ],
    plotOptions:{
        bar:{
            horizontal : false,
            datalabels:{
                position: 'top'
            }
        }
    },
    xaxis : {
        categories: ['Teste1','Teste2','Teste3','Teste4','Teste5','Teste6','Teste7']
    },
    yaxis: {
        min: 0,
        max:100,
        title: {
            text: 'Dados das Vendas de Hoje' 
        }
    },
    grid:{
        show: true,
        xaxis:{
            lines:{
                show: false
            }
        }
    },
    stroke:{
        width: 2,
        curve: 'smooth',
    },
    dataLabels: {
        enabled: true,
    },
    colors: ['#4466FF','#FF6688','#ffbb55']

}
let chart = new ApexCharts(el, options)
chart.render()


//btn grafico edit
let btn_graph = document.querySelectorAll('.btn_chart');
function activeBtnChart() {
    // body...
    var type = this.dataset.id;
    if(type === 'bar'){
        options.chart.type = "bar";
        chart.updateOptions(options);
    }else if(type === 'line'){
        options.chart.type = "line";
        chart.updateOptions(options);
    }else if(type === 'pie'){
        options.chart.type = "area";
        chart.updateOptions(options);
    }else{
        options.chart.type = "line";
        chart.updateOptions(options);
    }

    btn_graph.forEach((item) => 
    item.classList.remove('active'));
    this.classList.add('active');
}
btn_graph.forEach((item) => 
    item.addEventListener('click',activeBtnChart))




