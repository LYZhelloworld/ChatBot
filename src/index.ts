import ConsoleCommand from "./io/console-command";

async function main() {
  const consoleCommand = new ConsoleCommand();
  await consoleCommand.start();
}

main();
