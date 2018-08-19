public class RulesTable {

    volatile TableCell[][] table;

    RulesTable(int size) {
        table = new TableCell[size][size];

        for (int i = 0; i < size; i++) {
            for (int j = 0; j < size - i; j++) {
                table[i][j] = new TableCell(String.valueOf(i) + String.valueOf(j), false);
                table[i][j].xCor = i;
                table[i][j].yCor = j;
            }
        }

    }

    TableCell get(int i, int j) {
        return table[i][j];
    }

}
