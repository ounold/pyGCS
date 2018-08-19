import com.fasterxml.jackson.annotation.JsonProperty;

public class ProbabilityCell {

    static final ProbabilityCell EMPTY_CELL = new ProbabilityCell(-1.0, -1.0);

    @JsonProperty
    double item_1;
    @JsonProperty
    double item_2;

    ProbabilityCell() {

    }

    ProbabilityCell(double item_1, double item_2) {
        this.item_1 = item_1;
        this.item_2 = item_2;
    }
}
