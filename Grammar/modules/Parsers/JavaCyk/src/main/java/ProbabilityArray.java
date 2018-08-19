public class ProbabilityArray {

    ProbabilityCell[][][] table;

    ProbabilityArray(int sentenceLength, int nonTerminalSymbolsCount) {
        table = new ProbabilityCell[sentenceLength][sentenceLength][nonTerminalSymbolsCount];
        for (int i = 0; i < sentenceLength; i++) {
            for (int j = 0; j < sentenceLength - i; j++) {
                for (int k = 0; k < nonTerminalSymbolsCount; k++) {
                    table[i][j][k] = ProbabilityCell.EMPTY_CELL;
                }
            }
        }
    }

}
