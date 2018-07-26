Promise.all([
  fetch('Http://localhost:8000/data/parse_tree_final_data.json', {mode: 'no-cors'})
    .then(function(res) {
      return res.json()
    })
]).then(function(dataArray) {
    var cy = window.cy = cytoscape({
      container: document.getElementById('cy'),
      style: cytoscape.stylesheet().selector('node').css({
        'width': 'mapData(weight, 40, 80, 20, 60)',
        'content': 'data(name)',
        'text-valign': 'center',
        'text-outline-width': 2,
        'text-outline-color': 'data(faveColor)',
        'background-color': 'data(faveColor)',
        'color': '#fff',
        'opacity': 0.85
      }).selector('edge').css({
        'curve-style': 'bezier',
        'opacity': 0.666,
        'line-style': 'dotted',
        'width': 'mapData(strength, 70, 100, 2, 6)',
        'target-arrow-shape': 'triangle',
        'line-color': 'data(faveColor)',
        'source-arrow-color': 'data(faveColor)',
        'target-arrow-color': 'data(faveColor)'
      }).selector('.test').css({
        'width': 5,
        'border-color': '#333',
        'line-style': 'dashed',
      }),
      layout: {
        name: "dagre"
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