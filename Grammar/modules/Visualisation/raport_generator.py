import json
import os
import sys
import networkx
import random
from itertools import zip_longest


class ReportGenerator:
    def __init__(self, settings):
        self._path = "{}/../../../Charts/data/".format(os.path.dirname(os.path.abspath(__file__)))
        self._settings = settings
        self.iterations = 1
        self.collection_of_iterations = []
        self.collection_of_final_rules = []
        self.current_iteration = 0
        self.results = None
        self.rules = []
        self.tree = None
        self.final_rules = []

    def create_graphs(self):
        self._create_sensitivity_json(self.collection_of_iterations)
        self._create_specificity_json(self.collection_of_iterations)
        self._create_fitness_json(self.collection_of_iterations)
        self._create_precision_json(self.collection_of_iterations)
        self._create_grammar_size_json(self.collection_of_iterations)
        self._create_rules_json(self.collection_of_iterations)
        self._create_rules_description(self.collection_of_iterations)
        self.get_rules_parsing_negative_sentence(self.collection_of_iterations)
        self.graph = networkx.Graph()
        self.generate_final_tree(self.collection_of_final_rules[-1])
        self.generate_final_parse_tree(self.collection_of_final_rules[-1])

    def avg(self, x):
        x = [i for i in x if i is not None]
        return sum(x, 0.0) / len(x)

    def get_size(self, obj, seen=None):
        size = sys.getsizeof(obj)
        if seen is None:
            seen = set()
        obj_id = id(obj)
        if obj_id in seen:
            return 0
        seen.add(obj_id)
        if isinstance(obj, dict):
            size += sum([self.get_size(v, seen) for v in obj.values()])
            size += sum([self.get_size(k, seen) for k in obj.keys()])
        elif hasattr(obj, '__dict__'):
            size += self.get_size(obj.__dict__, seen)
        elif hasattr(obj, '__iter__') and not isinstance(obj, (str, bytes, bytearray)):
            size += sum([self.get_size(i, seen) for i in obj])
        return size

    def _create_sensitivity_json(self, iterations):
        iteration_list_all = []
        sensitivity_data_all = []
        trace_name = self._settings.get_value("general", "trace_name")
        hover_text_final = []
        for collection in iterations:
            iteration_list = []
            sensitivity_data = []
            for index, iteration in enumerate(collection.iterations):
                iteration_list.append(index+1)
                sensitivity_data.append(iteration.results.sensitivity)
            iteration_list_all.append(iteration_list)
            sensitivity_data_all.append(sensitivity_data)
        iteration_list_final = list(map(self.avg, zip_longest(*iteration_list_all)))
        sensitivity_data_final = list(map(self.avg, zip_longest(*sensitivity_data_all)))
        for index, sensitivity_value in enumerate(sensitivity_data_final):
            hover_text_final.append("{}|{:.2f}".format(index + 1, sensitivity_value))
        if os.path.exists("{}{}".format(self._path, "sensitivity.json")):
            with open("{}{}".format(self._path, "sensitivity.json"), "r") as f:
                parsed_file = json.load(f)
            parsed_file["data"].append({"x": iteration_list_final, "y": sensitivity_data_final,
                                        "text": hover_text_final, "type": "scatter", "hoverinfo": "none",
                                        "hovermode": "closest", "name": trace_name})
            with open("{}{}".format(self._path, "sensitivity.json"), "w") as f:
                f.write(json.dumps(parsed_file))
        else:
            result = {"data": [{"x": iteration_list_final, "y": sensitivity_data_final, "text": hover_text_final,
                                "type": "scatter", "hoverinfo": "none", "hovermode": "closest", "name": trace_name}],
                      "layout": {"title": "Sensitivity", "autosize": True,
                                 "xaxis": {"title": "Iterations"},
                                 "yaxis": {"title": "Sensitivity"}}}
            with open("{}{}".format(self._path, "sensitivity.json"), "w") as f:
                f.write(json.dumps(result))

    def _create_specificity_json(self, iterations):
        iteration_list_all = []
        specificity_data_all = []
        trace_name = self._settings.get_value("general", "trace_name")
        hover_text_final = []
        for collection in iterations:
            iteration_list = []
            specificity_data = []
            for index, iteration in enumerate(collection.iterations):
                iteration_list.append(index + 1)
                specificity_data.append(iteration.results.specificity)
            iteration_list_all.append(iteration_list)
            specificity_data_all.append(specificity_data)
        iteration_list_final = list(map(self.avg, zip_longest(*iteration_list_all)))
        specificity_data_final = list(map(self.avg, zip_longest(*specificity_data_all)))
        for index, specificity_value in enumerate(specificity_data_final):
            hover_text_final.append("{}|{:.2f}".format(index + 1, specificity_value))
        if os.path.exists("{}{}".format(self._path, "specificity.json")):
            with open("{}{}".format(self._path, "specificity.json"), "r") as f:
                parsed_file = json.load(f)
            parsed_file["data"].append({"x": iteration_list_final, "y": specificity_data_final,
                                        "text": hover_text_final, "type": "scatter", "hoverinfo": "none",
                                        "hovermode": "closest", "name": trace_name})
            with open("{}{}".format(self._path, "specificity.json"), "w") as f:
                f.write(json.dumps(parsed_file))
        else:
            result = {"data": [{"x": iteration_list_final, "y": specificity_data_final, "text": hover_text_final,
                                "type": "scatter", "hoverinfo": "none", "hovermode": "closest", "name": trace_name}],
                      "layout": {"title": "Specificity", "autosize": True,
                                 "xaxis": {"title": "Iterations"},
                                 "yaxis": {"title": "Specificity"}}}
            with open("{}{}".format(self._path, "specificity.json"), "w") as f:
                f.write(json.dumps(result))

    def _create_fitness_json(self, iterations):
        iteration_list_all = []
        fitness_data_all = []
        trace_name = self._settings.get_value("general", "trace_name")
        hover_text_final = []
        for collection in iterations:
            iteration_list = []
            fitness_data = []
            for index, iteration in enumerate(collection.iterations):
                iteration_list.append(index + 1)
                fitness_data.append(iteration.results.fitness)
            iteration_list_all.append(iteration_list)
            fitness_data_all.append(fitness_data)
        iteration_list_final = list(map(self.avg, zip_longest(*iteration_list_all)))
        fitness_data_final = list(map(self.avg, zip_longest(*fitness_data_all)))
        for index, fitness_value in enumerate(fitness_data_final):
            hover_text_final.append("{}|{:.2f}".format(index + 1, fitness_value))
        if os.path.exists("{}{}".format(self._path, "fitness.json")):
            with open("{}{}".format(self._path, "fitness.json"), "r") as f:
                parsed_file = json.load(f)
            parsed_file["data"].append({"x": iteration_list_final, "y": fitness_data_final,
                                        "text": hover_text_final, "type": "scatter", "hoverinfo": "none",
                                        "hovermode": "closest", "name": trace_name})
            with open("{}{}".format(self._path, "fitness.json"), "w") as f:
                f.write(json.dumps(parsed_file))
        else:
            result = {"data": [{"x": iteration_list_final, "y": fitness_data_final, "text": hover_text_final,
                                "type": "scatter", "hoverinfo": "none", "hovermode": "closest", "name": trace_name}],
                      "layout": {"title": "Fitness", "autosize": True,
                                 "xaxis": {"title": "Iterations"},
                                 "yaxis": {"title": "Fitness"}}}
            with open("{}{}".format(self._path, "fitness.json"), "w") as f:
                f.write(json.dumps(result))

    def _create_precision_json(self, iterations):
        iteration_list_all = []
        precision_data_all = []
        trace_name = self._settings.get_value("general", "trace_name")
        hover_text_final = []
        for collection in iterations:
            iteration_list = []
            precision_data = []
            for index, iteration in enumerate(collection.iterations):
                iteration_list.append(index + 1)
                precision_data.append(iteration.results.precision)
            iteration_list_all.append(iteration_list)
            precision_data_all.append(precision_data)
        iteration_list_final = list(map(self.avg, zip_longest(*iteration_list_all)))
        precision_data_final = list(map(self.avg, zip_longest(*precision_data_all)))
        for index, precision_value in enumerate(precision_data_final):
            hover_text_final.append("{}|{:.2f}".format(index + 1, precision_value))
        if os.path.exists("{}{}".format(self._path, "precision.json")):
            with open("{}{}".format(self._path, "precision.json"), "r") as f:
                parsed_file = json.load(f)
            parsed_file["data"].append({"x": iteration_list_final, "y": precision_data_final,
                                        "text": hover_text_final, "type": "scatter", "hoverinfo": "none",
                                        "hovermode": "closest", "name": trace_name})
            with open("{}{}".format(self._path, "precision.json"), "w") as f:
                f.write(json.dumps(parsed_file))
        else:
            result = {"data": [{"x": iteration_list_final, "y": precision_data_final, "text": hover_text_final,
                                "type": "scatter", "hoverinfo": "none", "hovermode": "closest", "name": trace_name}],
                      "layout": {"title": "Precision", "autosize": True,
                                 "xaxis": {"title": "Iterations"},
                                 "yaxis": {"title": "Precision"}}}
            with open("{}{}".format(self._path, "precision.json"), "w") as f:
                f.write(json.dumps(result))

    def _create_grammar_size_json(self, iterations):
        iteration_list_all = []
        grammar_size_all = []
        hover_text_final = []
        for collection in iterations:
            iteration_list = []
            grammar_size_data = []
            for index, iteration in enumerate(collection.iterations):
                iteration_list.append(index + 1)
                grammar_size_data.append(len(iteration.rules))
            iteration_list_all.append(iteration_list)
            grammar_size_all.append(grammar_size_data)
        iteration_list_final = list(map(self.avg, zip_longest(*iteration_list_all)))
        grammar_size_final = list(map(self.avg, zip_longest(*grammar_size_all)))
        for index, grammar_size in enumerate(grammar_size_final):
            hover_text_final.append("{}|{:.2f}".format(index + 1, grammar_size))
        result = {"data": [{"x": iteration_list_final, "y": grammar_size_final,
                            "text": hover_text_final, "type": "scatter",
                            "hoverinfo": "none", "hovermode": "closest"}],
                  "layout": {"title": "Grammar Size", "autosize": True,
                             "xaxis": {"title": "Iterations"},
                             "yaxis": {"title": "Size"}}}
        with open("{}{}".format(self._path, "grammar.json"), "w") as f:
            f.write(json.dumps(result))

    def _create_rules_json(self, iterations):
        trace_objects = []
        for index in range(4):
            y_objects = []
            text_objects = []
            trace_name = ""
            color = ""
            for iteration in iterations[-1].iterations:
                added_rules = []
                removed_rules = []
                terminal_rules = []
                non_terminal_rules = []
                rules_names = []
                for rule in iteration.added:
                    probability = "%.4f" % rule.rule.probability
                    rule_name = "{}->{}{}".format(str(rule.rule.left), (rule.rule.right1 or ""),
                                                  (rule.rule.right2 or ""))
                    if rule_name not in rules_names:
                        rules_names.append(rule_name)
                        rule_definition = "{}|{}|{};".format(rule_name, str(rule.rule.age), probability)
                        added_rules.append(rule_definition)
                rules_names = []
                for rule in iteration.removed:
                    probability = "%.4f" % rule.rule.probability
                    rule_name = "{}->{}{}".format(str(rule.rule.left), (rule.rule.right1 or ""),
                                                  (rule.rule.right2 or ""))
                    if rule_name not in rules_names:
                        rules_names.append(rule_name)
                        rule_definition = "{}|{}|{};".format(rule_name, str(rule.rule.age), probability)
                        removed_rules.append(rule_definition)
                for rule in iteration.terminal_rules_list:
                    probability = "%.4f" % rule.probability
                    rule_name = "{}->{}{}".format(str(rule.left), (rule.right1 or ""),
                                                  (rule.right2 or ""))
                    if rule_name not in rules_names:
                        rules_names.append(rule_name)
                        rule_definition = "{}|{}|{};".format(rule_name, str(rule.age), probability)
                        terminal_rules.append(rule_definition)
                for rule in iteration.non_terminal_rules_list:
                    probability = "%.4f" % rule.probability
                    rule_name = "{}->{}{}".format(str(rule.left), (rule.right1 or ""),
                                                  (rule.right2 or ""))
                    if rule_name not in rules_names:
                        rules_names.append(rule_name)
                        rule_definition = "{}|{}|{};".format(rule_name, str(rule.age), probability)
                        non_terminal_rules.append(rule_definition)
                if index == 0:
                    y_objects.append(len(added_rules))
                    text_objects.append("".join(added_rules))
                    trace_name = "Added rules"
                    color = "#2ba02c"
                elif index == 1:
                    y_objects.append(len(removed_rules))
                    text_objects.append("".join(removed_rules))
                    trace_name = "Removed rules"
                    color = "#d62829"
                if index == 2:
                    y_objects.append(len(terminal_rules))
                    text_objects.append("".join(terminal_rules))
                    trace_name = "Terminal rules"
                    color = "#ff7f0e"
                if index == 3:
                    y_objects.append(len(non_terminal_rules))
                    text_objects.append("".join(non_terminal_rules))
                    trace_name = "Non terminal rules"
                    color = "#1f76b4"
            trace_objects.append({
                "x": [x + 1 for x, _ in enumerate(iterations[-1].iterations)],
                "y": y_objects,
                "text": text_objects,
                "name": trace_name,
                "type": "bar",
                "hovermode": "closest",
                "hoverinfo": "none",
                "marker": {
                    "color": color,
                    "opacity": 0.8
                }
            })
        result = {"data": trace_objects, "layout": {"barmode": "stack"}}
        with open("{}{}".format(self._path, "rules_size.json"), "w") as f:
            f.write(json.dumps(result))

    def _create_rules_description(self, iterations):
        trace_objects = []
        for index in range(4):
            y_objects = []
            text_objects = []
            trace_name = ""
            color = ""
            for iteration in iterations[-1].iterations:
                initialization_rules = []
                covering_rules = []
                heuristic_rules = []
                unknown_rules = []
                rules_names = []
                for rule in iteration.rules:
                    probability = "%.4f" % rule.rule.probability
                    rule_name = "{}->{}{}".format(str(rule.rule.left), (rule.rule.right1 or ""),
                                                  (rule.rule.right2 or ""))
                    if rule_name not in rules_names:
                        rules_names.append(rule_name)
                        rule_definition = "{} -> {}{}|{}|{};".format(
                            str(rule.rule.left), (rule.rule.right1 or ""),
                            (rule.rule.right2 or ""), str(rule.rule.age), probability)
                        rule_origin = str(rule.rule.origin)
                        if rule_origin == "I":
                            initialization_rules.append(rule_definition)
                        if rule_origin == "C":
                            covering_rules.append(rule_definition)
                        if rule_origin == "H":
                            heuristic_rules.append(rule_definition)
                        if rule_origin == "U":
                            unknown_rules.append(rule_definition)
                if index == 0:
                    y_objects.append(len(initialization_rules))
                    text_objects.append("".join(initialization_rules))
                    trace_name = "Initialization rules"
                    color = "#1f76b4"
                if index == 1:
                    y_objects.append(len(covering_rules))
                    text_objects.append("".join(covering_rules))
                    trace_name = "Covering rules"
                    color = "#ff7f0e"
                if index == 2:
                    y_objects.append(len(heuristic_rules))
                    text_objects.append("".join(heuristic_rules))
                    trace_name = "Heuristic rules"
                    color = "#2ba02c"
                if index == 3:
                    y_objects.append(len(unknown_rules))
                    text_objects.append("".join(unknown_rules))
                    trace_name = "Unknown rules"
                    color = "#d62829"
            trace_objects.append({
                "x": [x + 1 for x, _ in enumerate(iterations[-1].iterations)],
                "y": y_objects,
                "text": text_objects,
                "name": trace_name,
                "type": "bar",
                "hovermode": "closest",
                "hoverinfo": "none",
                "marker": {
                    "color": color,
                    "opacity": 0.8
                }
            })
        result = {"data": trace_objects, "layout": {"barmode": "stack"}}
        with open("{}{}".format(self._path, "rules_description.json"), "w") as f:
            f.write(json.dumps(result))

    @staticmethod
    def get_color(symbol):
        if symbol == "$":
            return "#DB2B4E"
        elif symbol.islower():
            return "#302527"
        else:
            return "#B97463"

    @staticmethod
    def if_edge_exist(source, target, edges):
        # for edge in edges:
        #     if edge["data"]["source"] == source and edge["data"]["target"] == target:
        #         return True
        return False

    def generate_final_tree(self, rules):
        nodes = []
        edges = []
        rules_symbols = []
        rules_names = []
        count = 0
        average_usage = 0
        terminal_rules = 0
        color_list = ["#e6194b", "#3cb44b", "#ffe119", "#0082c8", "#f58231", "#911eb4",
                      "#46f0f0", "#f032e6", "#d2f53c", "#fabebe", "#008080", "#e6beff",
                      "#aa6e28", "#fffac8", "#800000", "#aaffc3", "#808000", "#ffd8b1",
                      "#000080", "#808080"]
        for rule in rules:
            rule_name = "{}->{}{}".format(str(rule.left),
                                          (rule.right1 or ""),
                                          (rule.right2 or ""))
            if rule_name not in rules_names:
                rules_names.append(rule_name)
                left = str(rule.left)
                right1 = str(rule.right1) if rule.right1 is not None else ""
                right2 = str(rule.right2) if rule.right2 is not None else ""
                if left not in rules_symbols:
                    if left != "":
                        rules_symbols.append(left)
                if right1 not in rules_symbols:
                    if right1 != "":
                        rules_symbols.append(right1)
                if right2 not in rules_symbols:
                    if right2 != "":
                        rules_symbols.append(right2)
                if right1 != "" and right2 == "":
                    if not self.if_edge_exist(left, right1, edges):
                        edges.append({"data": {"id": count, "weight": round(rule.probability, 2), "source": left,
                                               "target": right1, "faveColor": "#484848",
                                               "labelColor": "#262626",
                                               "selectedColor": "#4CABC1",
                                               "opacity": 0.1,
                                               "label": "{} -> {} P={:.2f}".format(left, right1,
                                                                                   round(rule.probability, 2))}})
                if right1 == "" and right2 != "":
                    if not self.if_edge_exist(left, right2, edges):
                        edges.append({"data": {"id": count, "weight": round(rule.probability, 2), "source": left,
                                               "target": right2, "faveColor": "#484848",
                                               "labelColor": "#fff",
                                               "selectedColor": "#293659",
                                               "opacity": 0.1,
                                               "label": "{} -> {} P={:.2f}".format(left, right2,
                                                                                   round(rule.probability, 2))}})
                if right1 != "" and right2 != "":
                    if not self.if_edge_exist(left, right1, edges):
                        edges.append({"data": {"id": count, "weight": round(rule.probability, 2), "source": left,
                                               "target": right1, "faveColor": "#484848",
                                               "selectedColor": "#4CABC1", "labelColor": "#262626",
                                               "opacity": 0.1,
                                               "label": "{} -> {}{} P={:.2f}".format(left, right1, right2,
                                                                                     round(rule.probability, 2))}})
                    count += 1
                    if not self.if_edge_exist(left, right2, edges):
                        edges.append({"data": {"id": count, "weight": round(rule.probability, 2), "source": left,
                                               "target": right2, "faveColor": "#484848",
                                               "selectedColor": "#293659", "labelColor": "#fff",
                                               "opacity": 0.1,
                                               "label": "{} -> {}{} P={:.2f}".format(left, right1, right2,
                                                                                     round(rule.probability, 2))}})
                count += 1
        for symbol in rules_symbols:
            count = 0
            if symbol.islower():
                terminal_rules += 1
            for edge in edges:
                if symbol == edge["data"]["source"]:
                    count += 1
            average_usage += count
            #print(average_usage)
            nodes.append({"data": {"id": symbol, "name": symbol, "faveColor": self.get_color(symbol),
                                   "score": count * 10}})
        average = average_usage/(len(rules_symbols) - terminal_rules)
        #print(average)
        for node in nodes:
            if node["data"]["score"] / 10 > average:
                generated_color = random.choice(color_list)
                color_list.remove(generated_color)
                for edge in edges:
                    if edge["data"]["source"] == node["data"]["name"]:
                        if node["data"]["name"] == '$':
                            generated_color = "#DB2B4E"
                        edge["data"]["faveColor"] = generated_color
                        edge["data"]["opacity"] = 1

        nodes.extend(edges)
        with open("{}{}".format(self._path, "parse_tree_data.json"), "w") as f:
            f.write(json.dumps(nodes))

    def get_rules_parsing_negative_sentence(self, iterations):
        trace_objects = []
        rules_objects = []
        invalid_rules_objects = []
        text_object = []
        for index, iteration in enumerate(iterations[-1].iterations):
            rules_names = []
            for data in iteration.sentence_rules_parsing_data:
                for rules_list in data[2]:
                    for rule_cell in [rule_cell for rule_cell in rules_list if rule_cell is not None]:
                        for rule in rule_cell:
                            if rule is not None:
                                rule_name = "{}->{}{}".format(str(rule.rule.left),
                                                              (rule.rule.right1 or ""),
                                                              (rule.rule.right2 or ""))
                                if rule_name not in rules_names:
                                    if data[1]:
                                        rules_names.append(rule_name)
            rules_objects.append(len(iteration.rules))
            invalid_rules_objects.append(len(rules_names))
            percent = (len(rules_names)/len(iteration.rules))*100
            text_object.append("{};{};{};{:.2f}".format(index + 1, len(iteration.rules), len(rules_names), percent))
        trace_objects.append({
            "x": [x + 1 for x, _ in enumerate(iterations[-1].iterations)],
            "y": rules_objects,
            "text": text_object,
            "name": "Number of rules",
            "type": "bar",
            "hovermode": "closest",
            "hoverinfo": "none",
            "marker": {
                "color": "green",
                "opacity": 0.8
            }
        })
        trace_objects.append({
            "x": [x + 1 for x, _ in enumerate(iterations[-1].iterations)],
            "y": invalid_rules_objects,
            "name": "Rules parsing negative sentences",
            "type": "scatter",
            "hovermode": "closest",
            "hoverinfo": "none",
            "marker": {
                "color": "red",
                "opacity": 0.8
            }
        })
        result = {"data": trace_objects, "layout": {}}
        with open("{}{}".format(self._path, "rules_negative_parsing.json"), "w") as f:
            f.write(json.dumps(result))

    def generate_edges(self, rules):
        for rule in rules:
            self.graph.add_edge(str(rule.left), str(rule.right1))
            if rule.right2 is not None:
                self.graph.add_edge(str(rule.left), str(rule.right2))
        try:
            self.tree = networkx.bfs_tree(self.graph, "$")
        except:
            pass

    def get_nodes_and_edges(self):
        edges = []
        nodes = []
        for parent, children in self.tree.edges._adjdict.items():
            for child in children.keys():
                edges.append({"data": {"id": "{}{}".format(parent, child), "weight": 1, "source": parent,
                                       "target": child, "faveColor": self.get_color(parent)}})
        for node in self.tree.nodes._nodes.keys():
            nodes.append({"data": {"id": node, "name": node, "faveColor": self.get_color(node)}})
        nodes.extend(edges)
        return nodes

    def generate_final_parse_tree(self, rules):
        self.generate_edges(rules)
        pass
        with open("{}{}".format(self._path, "parse_tree_final_data.json"), "w") as f:
            f.write(json.dumps(self.get_nodes_and_edges()))
