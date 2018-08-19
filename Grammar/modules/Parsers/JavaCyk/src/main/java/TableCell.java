import com.fasterxml.jackson.annotation.JsonProperty;

import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.atomic.AtomicBoolean;

public class TableCell {

    volatile AtomicBoolean evaluated = new AtomicBoolean(false);
    volatile String coordinates;
    volatile AtomicBoolean ruleFound = new AtomicBoolean(false);

    @JsonProperty
    volatile List<CellRule> rules = new ArrayList<>();

    volatile int xCor;
    volatile int yCor;

    boolean isNull;

    TableCell(String coordinates, boolean isNull) {
        this.coordinates = coordinates;
        this.isNull = isNull;
    }
}
