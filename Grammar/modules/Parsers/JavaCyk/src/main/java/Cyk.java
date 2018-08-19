import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import py4j.GatewayServer;

import java.io.IOException;
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.*;

public class Cyk {

    private static final int NUM_OF_THREADS = 4;

    static ConcurrentLinkedQueue<TableCell> jobs = new ConcurrentLinkedQueue<>();
    static ConcurrentLinkedQueue<RuleToAdd> rulesToAdd = new ConcurrentLinkedQueue<>();

    static RulesTable rulesTable;
    static ProbabilityArray probabilityArray;
    static Grammar grammar = new Grammar();

    static ExecutorService executors;

    void prepareJobs(int sentenceLength) {
        for (int i = 1; i < sentenceLength; i++) {
            for (int j = 0; j < sentenceLength - i; j++) {
                jobs.add(rulesTable.get(i, j));
            }
        }
    }

    static boolean parseSentence() {

        while (true) {
            TableCell cellToAnalyse = jobs.poll();

            if (cellToAnalyse == null) {
                return true;
            }

            int i = cellToAnalyse.xCor;
            int j = cellToAnalyse.yCor;

            boolean added = false;

            for (int k = 0; k < i; k++) {

                int parentOneI = k;
                int parentOneJ = j;

                int parentTwoI = i - k - 1;
                int parentTwoJ = j + k + 1;

                while (!rulesTable.table[parentOneI][parentOneJ].evaluated.get()
                        && !rulesTable.table[parentTwoI][parentTwoJ].evaluated.get()) {
                }


                for (Rule rule : grammar.rules) {
                    if (rule.right2 != null) {
                        int rule1index = rule.right1.index;
                        int rule2index = rule.right2.index;

                        if (probabilityArray.table[parentOneI][parentOneJ][rule1index] != ProbabilityCell.EMPTY_CELL
                                && probabilityArray.table[parentTwoI][parentTwoJ][rule2index] != ProbabilityCell.EMPTY_CELL) {

                            ProbabilityCell currentCell = probabilityArray.table[i][j][rule.left.index];
                            ProbabilityCell parentCellProbability = probabilityArray.table[parentOneI][parentOneJ][rule1index];
                            ProbabilityCell parent2CellProbability = probabilityArray.table[parentTwoI][parentTwoJ][rule2index];
                            probabilityArray.table[i][j][rule.left.index] = calculateProbability(currentCell, parentCellProbability, parent2CellProbability, rule);
                            rulesTable.table[i][j].rules.add(new CellRule(rule, new Coordinate(k, j), new Coordinate(i - k - 1, j + k + 1)));

                            if (!rulesTable.table[i][j].ruleFound.get()) {
                                rulesTable.table[i][j].ruleFound.compareAndSet(false, true);
                            }
                        }
                    }
                }

                if (!rulesTable.table[i][j].ruleFound.get() &&
                        rulesTable.table[k][j].ruleFound.get() &&
                        rulesTable.table[parentTwoI][parentTwoJ].ruleFound.get()) {
                    rulesToAdd.add(new RuleToAdd(i, j));
                    rulesTable.table[i][j].ruleFound.compareAndSet(false, true);
                }
            }
            rulesTable.table[i][j].evaluated.compareAndSet(false, true);
        }
    }

    static void initFirstRow(String sentence) {
        char[] chars = sentence.toCharArray();
        for (int i = 0; i < sentence.length(); i++) {
            for (Rule rule : grammar.rules) {
                if (rule.right1.value == chars[i]) {
                    rulesTable.table[0][i].rules.add(new CellRule(rule));
                    probabilityArray.table[0][i][rule.left.index] = new ProbabilityCell(rule.probability, rule.probability);
                }
            }
            rulesTable.table[0][i].evaluated.compareAndSet(false, true);
            rulesTable.table[0][i].ruleFound.compareAndSet(false, true);
        }

    }

    static ProbabilityCell calculateProbability(ProbabilityCell currentCell, ProbabilityCell parent1, ProbabilityCell parent2, Rule rule) {
        ProbabilityCell newProbabilityCell = new ProbabilityCell();
        if (currentCell.equals(ProbabilityCell.EMPTY_CELL)) {
            newProbabilityCell.item_1 = rule.probability * parent1.item_1 * parent2.item_1;
            newProbabilityCell.item_2 = rule.probability * parent1.item_2 * parent2.item_2;
        } else {
            newProbabilityCell.item_1 = currentCell.item_1 + (rule.probability * parent1.item_1 * parent2.item_2);
            newProbabilityCell.item_2 = currentCell.item_2 + (rule.probability * parent2.item_2 * parent2.item_2);
        }
        return newProbabilityCell;
    }

    public String runCyk(String testSentence, String jsonFile) {
        System.out.println(testSentence);

        ObjectMapper mapper = new ObjectMapper();
        try {
            grammar = mapper.readValue(jsonFile, Grammar.class);
        } catch (IOException e) {
            System.out.println("Ups " + e.getMessage());
            return null;
        }
        // Grammar values generation
        executors = Executors.newFixedThreadPool(NUM_OF_THREADS);

        List<Rule> rules = new ArrayList<>(grammar.nonTerminalRules);
        rules.addAll(grammar.terminalRules);
        grammar.rules = rules;

        // CYK parsing
        long startTime = System.currentTimeMillis();
        rulesTable = new RulesTable(testSentence.length());
        probabilityArray = new ProbabilityArray(testSentence.length(), grammar.nonTerminalSymbols.length);
        initFirstRow(testSentence);
        prepareJobs(testSentence.length());

        List<Callable<Object>> todo = new ArrayList<>();
        for (int i = 0; i < NUM_OF_THREADS; i++) {
            todo.add(Cyk::parseSentence);
        }
        try {
            List<Future<Object>> status = executors.invokeAll(todo);

            for (Future<Object> s : status) {
                s.get();
            }
        } catch (Exception e) {
            System.out.println("Exception occured: " + e.getMessage());
            executors.shutdownNow();
            return null;
        }
        executors.shutdown();

        long endTime = System.currentTimeMillis();
        long milis = endTime - startTime;
        long seconds = TimeUnit.MILLISECONDS.toSeconds(milis);
        milis = milis - seconds * 1000;

        String rulesTableJson = "";
        String probabilityTableJson = "";
        String rulesToAddStr = "";
        try {
            rulesTableJson = mapper.writeValueAsString(rulesTable.table);
            probabilityTableJson = mapper.writeValueAsString(probabilityArray.table);
            rulesToAddStr = mapper.writeValueAsString(rulesToAdd);
        } catch (JsonProcessingException e) {
            e.printStackTrace();
        }

        System.out.println("s: " + seconds + " + ms:" + milis);
        rulesToAdd.clear();
        return "{ \"rules_table\": " + rulesTableJson + ", \"probability_table\": " + probabilityTableJson + ", \"rules_to_add\": " + rulesToAddStr + "}";
    }

    public static void main(String... args) {
        Cyk app = new Cyk();
        GatewayServer server = new GatewayServer(app);
        server.start();
    }

}
