let plotDiv = document.getElementById("graph-container");
let rulesInfoDiv = document.getElementById('rules-body');
let rulesHeaderTable = document.getElementById('rules-header');
var test = undefined;

Plotly.d3.json("http://localhost:8000/data/rules_size.json", function(error, result) {
    // plotDiv.layout.hovermode = "closest";
    Plotly.plot(plotDiv, result.data, result.layout);
    plotDiv.on('plotly_hover', function(result) {
        var infotext = result.points.map((bar) => {
            var content = "";
            let rules = bar.text.split(";").filter((x) => {
                return (x !== (undefined || null || ""))
            });
            for (let index in rules) {
                let rules_object = rules[index].split("|").filter((x) => {
                    return (x !== (undefined || null || ""))
                });
                let rule = rules_object[0];
                let age = rules_object[1];
                let probability = rules_object[2];
                content += `<tr><td>${rule}</td><td>${age}</td><td>${probability}</td></tr>`
            }
            rulesHeaderTable.removeAttribute("class");
            if (bar.data.name == "Added rules") {
                rulesHeaderTable.classList.add("added-th");
                return `<table id="rules-body" class="added-td">${content}</table>`;
            } else if (bar.data.name == "Removed rules") {
                rulesHeaderTable.classList.add("removed-th");
                return `<table id="rules-body" class="removed-td">${content}</table>`;
            } else if (bar.data.name == "Terminal rules") {
                rulesHeaderTable.classList.add("terminal-th");
                return `<table id="rules-body" class="terminal-td">${content}</table>`;
            } else {
                rulesHeaderTable.classList.add("non-terminal-th");
                return `<table id="rules-body" class="non-terminal-td">${content}</table>`;
            }
        });
        rulesInfoDiv.innerHTML = infotext;
    });
});

window.onresize = function() {
    Plotly.Plots.resize(plotDiv);
};


