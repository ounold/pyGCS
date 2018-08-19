import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.Data;

@Data
public class CellRule {

    @JsonProperty
    private Rule rule;

    @JsonProperty
    private Coordinate cell1Coordinates;

    @JsonProperty
    private Coordinate cell2Coordinates;

    @JsonProperty
    private Coordinate rootCellCoordinates;

    public CellRule() {

    }

    public CellRule(Rule rule) {
        this.rule = rule;
    }

    public CellRule(Rule rule, Coordinate c1, Coordinate c2) {
        this.rule = rule;
        this.cell1Coordinates = c1;
        this.cell2Coordinates = c2;
    }

}
