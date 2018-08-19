import com.fasterxml.jackson.annotation.JsonProperty;

public class Rule {

    @JsonProperty
    Symbol left;
    @JsonProperty
    Symbol right1;
    @JsonProperty
    Symbol right2;
    @JsonProperty
    double probability = Math.random();

    public Rule() {
    }

    public Rule(Symbol left, Symbol right1, Symbol right2, double probability) {
        this.left = left;
        this.right1 = right1;
        this.right2 = right2;
        this.probability = probability;
    }

    @Override
    public String toString() {
        return left.toString() + "->" + right1.toString() + right2.toString();
    }
}
