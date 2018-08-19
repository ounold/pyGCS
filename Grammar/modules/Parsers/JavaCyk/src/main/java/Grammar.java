import com.fasterxml.jackson.annotation.JsonIgnore;
import com.fasterxml.jackson.annotation.JsonProperty;

import java.util.List;

public class Grammar {

    @JsonIgnore
    List<Rule> rules;

    @JsonProperty
    List<Rule> terminalRules;
    @JsonProperty
    List<Rule> nonTerminalRules;
    @JsonProperty
    Symbol[] nonTerminalSymbols;
    @JsonProperty
    Symbol[] terminalSymbols;

}
