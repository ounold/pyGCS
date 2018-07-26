Promise.all([
  fetch('Http://localhost:8000/data/parse_tree_data.json', {mode: 'no-cors'})
    .then(function(res) {
      return res.json()
    })
]).then(function(dataArray) {
    var cy = window.cy = cytoscape({
      container: document.getElementById('cy'),
      style: cytoscape.stylesheet().selector('node').css({
        "width": "mapData(score, 0, 100, 30, 100)",
        "height": "mapData(score, 0, 100, 30, 100)",
        'content': 'data(name)',
        'text-valign': 'center',
        'font-size': 30,
        "z-index":10,
        'text-outline-width': 2,
        'text-outline-color': 'data(faveColor)',
        'background-color': 'data(faveColor)',
        'color': '#fff',
        'opacity': 0.85
      }).selector('edge').css({
        'curve-style': 'bezier',
        "loop-direction": -90,
        "loop-sweep": 55,
        "control-point-step-size": 100,
        'line-style': 'dotted',
        'opacity': 'data(opacity)',
        'width': 'mapData(weight, 0.0, 1.0, 2, 8)',
        'target-arrow-shape': 'triangle',
        'line-color': 'data(faveColor)',
        'source-arrow-color': 'data(faveColor)',
        'target-arrow-color': 'data(faveColor)'
      }).selector('.test').css({
        'width': 5,
        'border-color': '#333',
        'line-style': 'solid',
        'opacity': 0.800,
        'width': 'mapData(weight, 0, 100, 1, 10)',
        "label": "data(label)",
        'line-color': 'data(selectedColor)',
        'source-arrow-color': 'data(selectedColor)',
        'target-arrow-color': 'data(selectedColor)',
        "font-size": 25,
        'font-style': "italic",
        "text-outline-color": "data(selectedColor)",
        "text-outline-width": 3,
        "color": "data(labelColor)",
        'z-index': 10000,
      }),
      layout: {
        name: "circle"
      },
      elements: dataArray[0],
    });
    cy.on('mouseover', 'node', function(evt) {
      var node = this;
        var connectedEdges = node.connectedEdges();
        connectedEdges.forEach(function(edge) {
            if(edge.data()["source"] == evt.target.id()) {
                edge.addClass("test")
            }
        })
    });

    cy.on('mouseout', 'node', function(evt) {
      var node = this;
        var connectedEdges = node.connectedEdges();
        connectedEdges.forEach(function(edge) {
            if(edge.data()["source"] == evt.target.id()) {
                edge.removeClass("test")
            }
        })
    });
  });
