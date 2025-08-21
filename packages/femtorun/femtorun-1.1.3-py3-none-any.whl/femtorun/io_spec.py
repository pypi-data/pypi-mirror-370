import yaml
import networkx as nx
from typing import *
from femtorun.io_spec_data import check_IOSpecData, IOSpecData


class IOSpec:
    def __init__(self, fname_or_data=Union[str, IOSpecData]):
        """IOSpec adds utility methods around the IO spec file contents,
        and has methods to allow an IO spec to be written programatically

        args:
            fname_or_data:
                either the filename of the yaml to initialize from,
                or an already-constructed data dict
        """

        if isinstance(fname_or_data, str):
            self.data: dict = yaml.safe_load(open(fname_or_data, "r"))
        else:
            self.data = fname_or_data

        check_IOSpecData(self.data)

        # "simple" specs are 1:1 inputs:outputs
        # used by legacy femtorunner APIs
        self.is_simple: bool = (
            False  # whether or not the spec only has a single simple_sequence
        )
        self.simple_action: Optional[
            str
        ] = None  # name of the graph node that represents the simple action
        self.simple_inputs: Optional[list[str]] = None
        self.simple_outputs: Optional[list[str]] = None

        # as long as variables can have un-yaml'able names,
        # we need a varname field and need these
        self.node_to_var: dict[str, str] = {}
        self.var_to_node: dict[str, str] = {}

        # dataflow graph, shows dependencies encoded by sequences
        self.G: nx.DiGraph = nx.DiGraph()
        self._init_graph()

    def _init_graph(self) -> nx.DiGraph:
        """processes the IO graph into a networkx digraph,
        checks dagness, can be used to make plots"""
        self._set_if_simple()
        self._make_G()
        self._verify_dag()

    def _set_if_simple(self):
        """if the spec only contains a single simple_sequence,
        (or something equivalent to it) it is "simple",
        and can be processed using the legacy FR APIs"""
        self.is_simple = True
        self.simple_action = None

        # fail if any complex sequences with more than frequency 1
        for objname, obj in self.data.items():
            if obj["type"] == "complex_sequence":
                for io, val in obj["inputs"].items():
                    if val > 1:
                        self.is_simple = False
                        return
                for io, val in obj["outputs"].items():
                    if val > 1:
                        self.is_simple = False
                        return

        # fail if there's more than one sequence
        # ignore sequences with no outputs
        # these are likely parameter-setting
        seq_ct = 0
        for objname, obj in self.data.items():
            if "sequence" in obj["type"] and len(obj["outputs"]) > 0:
                seq_ct += 1

        if seq_ct != 1:
            self.is_simple = False
            return

        # fell through, we made it
        # find what should be the only sequence, record that action name
        # can use this later to figure out the "relevant" inputs for step
        for objname, obj in self.data.items():
            if "sequence" in obj["type"]:
                self.simple_action = objname
                # collect dict keys or just copy the list
                self.simple_inputs = list(obj["inputs"])
                self.simple_outputs = list(obj["outputs"])

    def _make_G(self):
        """process the yaml's Sequences into a Graph"""

        # nodes first
        for objname, obj in self.data.items():
            if obj["type"] in ["input", "output"]:
                varname = obj["varname"]
                assert objname not in self.node_to_var
                assert varname not in self.var_to_node
                self.node_to_var[objname] = varname
                self.var_to_node[varname] = objname

                self.G.add_node(objname, attr=obj)

        # then sequences, which are like edges
        for objname, obj in self.data.items():
            if obj["type"] in ["input", "output"]:
                pass
            elif obj["type"] == "simple_sequence":
                action = objname
                self.G.add_node(action)  # no attributes

                for o in obj["outputs"]:
                    self.G.add_edge(action, o, frequency=1)
                for i in obj["inputs"]:
                    self.G.add_edge(i, action, frequency=1)

            elif obj["type"] == "complex_sequence":
                action = objname
                self.G.add_node(action)  # no attributes

                for o, ct in obj["outputs"].items():
                    self.G.add_edge(action, o, frequency=ct)
                for i, ct in obj["inputs"].items():
                    self.G.add_edge(i, action, frequency=ct)

            else:
                raise ValueError(f"IO spec entry {objname} had undefined type")

    def __str__(self):
        r = [str(self.G), "edges:"]
        for edge in self.G.edges.data():
            r.append(str(edge))
        return "\n".join(r)

    def _verify_dag(self):
        """make sure the graph is DAG"""
        # verify DAG-ness
        if not nx.is_directed_acyclic_graph(self.G):
            raise ValueError("IO spec does not contain a graph without cycles")
        # can dump graph plot

    def _get_io_padding(self, io_type) -> dict[str, tuple[int, int]]:
        pad_dict = {}
        for objname, obj in self.data.items():
            if obj["type"] == io_type:
                pad_dict[obj["varname"]] = ((obj["length"],), (obj["padded_length"],))
        return pad_dict

    @property
    def input_padding(self):
        return self._get_io_padding("input")

    @property
    def output_padding(self):
        return self._get_io_padding("output")

    # sim_* calls comprise a degenerate Femtorunner
    # doesn't do any math, but knows what outputs follow
    # from which inputs

    def sim_reset(self):
        """reset execution model state
        sets the count attribute on each edge to 0
        """
        for edge in self.G.edges():
            self.G.edges[edge]["count"] = 0

    def _recurse_node(self, node: str):
        # increment outgoing edge scores by 1, see if each child is satisfied
        # recurse if this is the case
        # also check that we don't see count > freq
        # this isn't the most efficient solution,
        #  but it's simple, and these graphs are very small
        for succ in self.G.successors(node):
            # increment count on edge towards each child
            edge = (node, succ)
            self.G.edges[edge]["count"] += 1

            # look back towards all that child's parents
            # see if it's fully satisfied (freq == count)
            satisfied = True
            for pred in self.G.predecessors(succ):
                edge = (pred, succ)
                if self.G.edges[edge]["count"] > self.G.edges[edge]["frequency"]:
                    raise RuntimeError(
                        "Bad input sequence, provided too many inputs before receiving outputs"
                    )
                if self.G.edges[edge]["count"] < self.G.edges[edge]["frequency"]:
                    satisfied = False

            if satisfied:
                # recurse
                self._recurse_node(succ)

                # reset, but not if output
                # outputs are cleared with sim_recv_outputs
                if self.data[succ]["type"] != "output":
                    for pred in self.G.predecessors(succ):
                        edge = (pred, succ)
                        self.G.edges[edge]["count"] = 0

    def sim_send_inputs(self, inputs: list[str]):
        """figure out which actions/outputs are triggered when these inputs are sent"""
        for inp in inputs:
            obj = self.var_to_node[inp]
            assert obj in self.G.nodes()  # must be a named node
            assert self.G.in_degree(obj) == 0  # must be an input node
            self._recurse_node(obj)

    def sim_recv_outputs(self) -> list[str]:
        """clear triggered outputs"""
        outputs = []

        for node in self.G.nodes():
            if self.data[node]["type"] == "output":
                # this is an output
                # there should be only one pred
                assert self.G.out_degree(node) == 0
                assert self.G.in_degree(node) == 1
                pred = next(iter(self.G.predecessors(node)))
                edge = (pred, node)
                if self.G.edges[edge]["count"] == self.G.edges[edge]["frequency"]:
                    # add to list and reset
                    outputs.append(self.node_to_var[node])
                    self.G.edges[edge]["count"] = 0

        return outputs

    def write_spec_to_file(self, fname: str):
        """dump completed IO spec to file"""

        class SpaceDumper(yaml.SafeDumper):
            # insert blank lines between top-level objects
            def write_line_break(self, data=None):
                super().write_line_break(data)
                if len(self.indents) == 1:
                    super().write_line_break()

        yaml.dump(self.data, open(fname, "w"), Dumper=SpaceDumper, sort_keys=False)


class IOSpecLegacyPadding:
    def __init__(self, input_padding, output_padding):
        """Just used in interim period while we are moving to IOSpec-initialization
        returns None for recv_outputs,
        derived runners should not check names actually received against None
        """
        self.input_padding = self._shapeify(input_padding)
        self.output_padding = self._shapeify(output_padding)
        self.is_simple = True

    @staticmethod
    def _shapeify(padding):
        """some runners pass {k : (int, int)} for 1d instead of {k : ((int,), (int,))}"""
        if padding is None:
            return None

        to_shape = {}
        for k, (true_shape, padded_shape) in padding.items():
            if isinstance(true_shape, int):
                to_shape[k] = ((true_shape,), (padded_shape,))
            else:
                to_shape[k] = (true_shape, padded_shape)
        return to_shape

    def sim_send_inputs(self, *args, **kwargs):
        pass

    def sim_recv_outputs(self, *args, **kwargs):
        return None

    def sim_reset(self, *args, **kwargs):
        pass
