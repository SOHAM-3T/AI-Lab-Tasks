import java.util.*;

class EightPuzzleBFS {

    static class Node {
        String state;  
        String path;
        Node(String state, String path) {
            this.state = state;
            this.path = path;
        }
    }

    static int[][] moves = {
        {-1, 0},
        {1, 0},
        {0, -1},
        {0, 1}
    };

    static void printMatrix(String state) {
        for (int i = 0; i < 9; i++) {
            System.out.print(state.charAt(i) + " ");
            if ((i + 1) % 3 == 0) System.out.println();
        }
        System.out.println();
    }

    public static String bfs(String start, String goal) {
        Queue<Node> queue = new LinkedList<>();
        Set<String> visited = new HashSet<>();
        queue.add(new Node(start, start));
        visited.add(start);

        while (!queue.isEmpty()) {
            Node current = queue.poll();

            if (current.state.equals(goal)) {
                return current.path;
            }

            int zeroIndex = current.state.indexOf('0');
            int row = zeroIndex / 3;
            int col = zeroIndex % 3;

            for (int[] move : moves) {
                int newRow = row + move[0];
                int newCol = col + move[1];

                if (newRow >= 0 && newRow < 3 && newCol >= 0 && newCol < 3) {
                    char[] newStateArr = current.state.toCharArray();
                    int newZeroIndex = newRow * 3 + newCol;

                    char temp = newStateArr[zeroIndex];
                    newStateArr[zeroIndex] = newStateArr[newZeroIndex];
                    newStateArr[newZeroIndex] = temp;

                    String newState = new String(newStateArr);

                    if (!visited.contains(newState)) {
                        visited.add(newState);
                        queue.add(new Node(newState, current.path + "," + newState));
                    }
                }
            }
        }
        return null;
    }

    public static int countInversions(String puzzle) {
        int[] arr = new int[9];
        int idx = 0;
        for (char c : puzzle.toCharArray()) {
            arr[idx++] = c - '0';
        }
        int inversions = 0;
        for (int i = 0; i < 9; i++) {
            for (int j = i + 1; j < 9; j++) {
                if (arr[i] != 0 && arr[j] != 0 && arr[i] > arr[j]) {
                    inversions++;
                }
            }
        }
        return inversions;
    }

    public static boolean isSolvable(String start, String goal) {
        return (countInversions(start)%2) == (countInversions(goal)%2);
    }

    public static void main(String[] args) {
        Scanner scanner = new Scanner(System.in);
        System.out.print("Enter the string puzzle :");// String start = "724506831";
        String start = scanner.nextLine();
        System.out.print("Enter the string goal :");// String goal = "012345678";
        String goal = scanner.nextLine();

        if (!isSolvable(start, goal)) {
            System.out.println("This puzzle is NOT solvable.");
        } else {
            String result = bfs(start, goal);
            if (result == null) {
                System.out.println("No solution found.");
            } else {
                String[] states = result.split(",");
                for (String state : states) {
                    printMatrix(state);
                }
                System.out.println("Total moves required: " + (states.length - 1));
            }
        }
    }
}
