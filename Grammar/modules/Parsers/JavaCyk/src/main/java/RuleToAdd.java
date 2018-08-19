import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.AllArgsConstructor;
import lombok.Data;

@Data
@AllArgsConstructor
public class RuleToAdd {
    @JsonProperty
    int i;

    @JsonProperty
    int j;
}
