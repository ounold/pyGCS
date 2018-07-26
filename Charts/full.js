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

Plotly.d3.json("http://localhost:8000/data/full_params.json", function(error, result) {
    Plotly.plot(plotDiv, result.data, result.layout);
    var tableContent = '<table id="rules-body" class="full-data">';
    for (var data_index in result.data) {
        if (result.data[data_index].name === "Sensitivity") {
            for (var text_index in result.data[data_index].text) {
                let iterations = result.data[data_index].text[text_index].split("|");
                let iteration = iterations[0];
                let sensitivity = iterations[1];
                let specificity = iterations[2];
                let fitness = iterations[3];
                let precision = iterations[4];
                tableContent += `<tr id="row_${iterations[0]}"><td>${iteration}</td><td>${sensitivity}</td><td>${specificity}</td><td>${fitness}</td><td>${precision}</td></tr>`
            }
        }
    }
    rulesInfoDiv.innerHTML = tableContent + "</table>";
    plotDiv.on('plotly_hover', function(result) {
        var number = result.points.map((data) => {
            if (data.data.name === "Sensitivity") {
                let iterations = data.text.split("|");
                let iteration = iterations[0];
                return iteration;
            }
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


