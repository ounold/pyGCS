function init(name) {
    let plotDiv = document.getElementById("graph-container");
    let rulesInfoDiv = document.getElementById('rules-body');
    let rulesHeaderTable = document.getElementById('rules-header');
    let leftArrow = document.getElementById('left-arrow');
    let rightArrow = document.getElementById('right-arrow');
    let traceName = document.getElementById('chosen-trace-name');
    function checkIfInView(element){
        var offset = (element.offset().top - 50) - ($("#rules-body").scrollTop());
        if(Math.abs(offset) > ($("#rules-body").height() - 70)){
            $('#rules-body').animate({scrollTop: offset}, 100);
            return false;
        }
       return true;
    }
    Plotly.d3.json("http://localhost:8000/data/" + name + ".json", function(error, result) {
        Plotly.plot(plotDiv, result.data, result.layout);
        let arrayLength = result.data.length;
        let currentIndex = 0;
        var tableContent = '<table id="rules-body" class="data_result">';
        for (var text_index in result.data[currentIndex].text) {
            let iterations = result.data[currentIndex].text[text_index].split("|");
            let iteration = iterations[0];
            let data_result = iterations[1];
            tableContent += `<tr id="row_${iterations[0]}"><td>${iteration}</td><td>${data_result}</td></tr>`
        }
        traceName.innerHTML = result.data[currentIndex].name;
        rulesInfoDiv.innerHTML = tableContent + "</table>";
        if (arrayLength === 1) {
            rightArrow.classList.add("right-arrow-unused");
            leftArrow.classList.add("left-arrow-unused");
        }
        leftArrow.onclick = function() {
            if (currentIndex !== 0) {
                tableContent = '<table id="rules-body" class="data_result">';
                currentIndex -= 1;
                for (var text_index in result.data[currentIndex].text) {
                    let iterations = result.data[currentIndex].text[text_index].split("|");
                    let iteration = iterations[0];
                    let data_result = iterations[1];
                    tableContent += `<tr id="row_${iterations[0]}"><td>${iteration}</td><td>${data_result}</td></tr>`
                }
                traceName.innerHTML = result.data[currentIndex].name;
                rulesInfoDiv.innerHTML = tableContent + "</table>";
            }
            if (currentIndex === 0) {
                leftArrow.classList.add("left-arrow-unused");
            } else {
                leftArrow.classList.remove("left-arrow-unused");
            }
            if (currentIndex === arrayLength - 1) {
                rightArrow.classList.add("right-arrow-unused");
            } else {
                rightArrow.classList.remove("right-arrow-unused");
            }
        };
        rightArrow.onclick = function() {
            if (currentIndex !== arrayLength - 1) {
                tableContent = '<table id="rules-body" class="data_result">';
                currentIndex += 1;
                for (var text_index in result.data[currentIndex].text) {
                    let iterations = result.data[currentIndex].text[text_index].split("|");
                    let iteration = iterations[0];
                    let data_result = iterations[1];
                    tableContent += `<tr id="row_${iterations[0]}"><td>${iteration}</td><td>${data_result}</td></tr>`
                }
                traceName.innerHTML = result.data[currentIndex].name;
                rulesInfoDiv.innerHTML = tableContent + "</table>";
            }
            if (currentIndex === arrayLength - 1) {
                rightArrow.classList.add("right-arrow-unused");
            } else {
                rightArrow.classList.remove("right-arrow-unused");
            }
            if (currentIndex === 0) {
                leftArrow.classList.add("left-arrow-unused");
            } else {
                leftArrow.classList.remove("left-arrow-unused");
            }
        };
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
            let chosenRow = document.getElementById("row_" + clearNumber[0]);
            checkIfInView($('#row_' + clearNumber));
            chosenRow.classList.add("chosen-row");
        });
    });
    window.onresize = function() {
        Plotly.Plots.resize(plotDiv);
    };
}

