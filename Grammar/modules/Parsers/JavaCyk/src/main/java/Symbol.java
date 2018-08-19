import com.fasterxml.jackson.annotation.JsonProperty;

public class Symbol {

    @JsonProperty
    char value;

    @JsonProperty
    int index;

    Symbol() {

    }

    Symbol(char value, int index) {
        this.value = value;
        this.index = index;
    }

    @Override
    public String toString() {
        return String.valueOf(value);
    }
}
