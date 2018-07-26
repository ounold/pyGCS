let plotDiv = document.getElementById("graph-container");
let rulesInfoDiv = document.getElementById('rules-body');
let rulesHeaderTable = document.getElementById('rules-header');
var test = undefined;

Plotly.d3.json("http://localhost:8000/data/rules_description.json", function(error, result) {
    // plotDiv.layout.hovermode = "closest";
    Plotly.plot(plotDiv, result.data, result.layout);
    plotDiv.on('plotly_hover', function(result) {
        var infotext = result.points.map((bar) => {
            var content = "";
            let rules = bar.text.split(";").filter((x) => {
                return (x !== (undefined || null || ""))
            });
            for (let index in rules) {
                let rule = rules[index].split("|").filter((x) => {
                    return (x !== (undefined || null || ""))
                });
                let ruleDefinition = rule[0];
                let ruleAge = rule[1];
                let ruleProbability = rule[2];
                content += `<tr><td>${ruleDefinition}</td><td>${ruleAge}</td><td>${ruleProbability}</td></tr>`
            }
            rulesHeaderTable.removeAttribute("class");
            if (bar.data.name == "Covering rules") {
                rulesHeaderTable.classList.add("covering-th");
                return `<table id="rules-body" class="covering-td">${content}</table>`;
            } else if (bar.data.name == "Heuristic rules") {
                rulesHeaderTable.classList.add("heuristic-th");
                return `<table id="rules-body" class="heuristic-td">${content}</table>`;
            } else if (bar.data.name == "Initialization rules") {
                rulesHeaderTable.classList.add("init-th");
                return `<table id="rules-body" class="init-td">${content}</table>`;
            } else {
                rulesHeaderTable.classList.add("unknown-th");
                return `<table id="rules-body" class="unknown-td">${content}</table>`;
            }
        });
        rulesInfoDiv.innerHTML = infotext;
    });
});

window.onresize = function() {
    Plotly.Plots.resize(plotDiv);
};


