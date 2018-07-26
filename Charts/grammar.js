let plotDiv = document.getElementById("graph-container");
let rulesInfoDiv = document.getElementById('rules-body');
let rulesHeaderTable = document.getElementById('rules-header');

function checkIfInView(element){
    var offset = (element.offset().top - 50) - ($("#rules-body").scrollTop());
    if(Math.abs(offset) > ($("#rules-body").height() - 70)){
        $('#rules-body').animate({scrollTop: offset}, 100);
        return false;
    }
   return true;
}

Plotly.d3.json("http://localhost:8000/data/grammar.json", function(error, result) {
    Plotly.plot(plotDiv, result.data, result.layout);
    var tableContent = '<table id="rules-body" class="grammar">';
    for (var data_index in result.data) {
        for (var text_index in result.data[data_index].text) {
            let iterations = result.data[data_index].text[text_index].split("|");
            let iteration = iterations[0];
            let grammar = iterations[1];
            tableContent += `<tr id="row_${iterations[0]}"><td>${iteration}</td><td>${grammar}</td></tr>`
        }
    }
    rulesInfoDiv.innerHTML = tableContent + "</table>";
    plotDiv.on('plotly_hover', function(result) {
        var number = result.points.map((data) => {
            let iterations = data.text.split("|");
            let iteration = iterations[0];
            return iteration;
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
