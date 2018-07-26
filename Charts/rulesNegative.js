let plotDiv = document.getElementById("graph-container");
let rulesInfoDiv = document.getElementById('rules-body');
let rulesHeaderTable = document.getElementById('rules-header');
var test = undefined;

function checkIfInView(element){
    var offset = (element.offset().top - 50) - ($("#rules-body").scrollTop());
    if(Math.abs(offset) > ($("#rules-body").height() - 70)){
        $('#rules-body').animate({scrollTop: offset}, 100);
        return false;
    }
   return true;
}

Plotly.d3.json("http://localhost:8000/data/rules_negative_parsing.json", function(error, result) {
    // plotDiv.layout.hovermode = "closest";
    Plotly.plot(plotDiv, result.data, result.layout);
    var tableContent = '<table id="rules-body" class="negative">';
    console.log(result.data);
    for (var text_index in result.data[0].text) {
        let data = result.data[0].text[text_index].split(";");
        let iteration = data[0];
        let rulesNumber = data[1];
        let rulesNegative = data[2];
        let percentage = data[3];
        tableContent += `<tr id="row_${iteration}"><td>${iteration}</td><td>${rulesNumber}</td><td>${rulesNegative}</td><td>${percentage}</td></tr>`
    }
    rulesInfoDiv.innerHTML = tableContent + "</table>";
    plotDiv.on('plotly_hover', function(result) {
        var number = result.points.map((data) => {
            console.log(data);
            let iterations = data.text.split(";");
            return iterations[0];
        });
        let clearNumber = number.filter((x) => {
            return (x !== undefined)
        });
        let allRows = document.querySelectorAll('[id^="row_"]');
        for (var row_index in allRows) {
            if (allRows[row_index].id !== undefined) {
                var next_row = document.getElementById(allRows[row_index].id);
                next_row.classList.remove("chosen-row");
            }
        }
        let chosenRow = document.getElementById("row_" + clearNumber);
        checkIfInView($('#row_' + clearNumber));
        chosenRow.classList.add("chosen-row");
    });
});

window.onresize = function() {
    Plotly.Plots.resize(plotDiv);
};


