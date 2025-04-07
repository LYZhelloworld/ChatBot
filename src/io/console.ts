import readline from "node:readline";

export default class ConsoleIO {
  private static readonly MULTILINE_TAGS = ["'''", '"""'];
  private static readonly INPUT_PROMPT = ">>> ";
  private static readonly INPUT_MULTILINE_PROMPT = "... ";

  /**
   * Accept user input with support for single-line and multi-line modes.
   *
   * Single-line mode is triggered by input other than triple single quotes or triple double quotes.
   *
   * Multi-line mode is triggered by triple single quotes or triple double quotes and ends when the same is entered again.
   */
  input(): Promise<string> {
    const rl = readline.createInterface({
      input: process.stdin,
      output: process.stdout,
    });

    return new Promise((resolve) => {
      rl.question(ConsoleIO.INPUT_PROMPT, (inputContent) => {
        if (ConsoleIO.MULTILINE_TAGS.includes(inputContent)) {
          const tag = inputContent;
          const lines: string[] = [];
          rl.question(ConsoleIO.INPUT_MULTILINE_PROMPT, (line) => {
            if (line != tag) {
              lines.push(line);
            } else {
              resolve(lines.join("\n"));
            }
          });
        } else {
          resolve(inputContent);
        }
      });
    });
  }
}
