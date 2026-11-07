from database import init_database
from coordinator import Coordinator
from tools.task_tools import list_tasks, check_overdue, task_summary


def main():
    init_database()
    coordinator = Coordinator()
    print('Meeting Action AI Agent | Qwen3 via Ollama')
    while True:
        print('\n1 Analyze meeting  2 Clarify pending  3 Save approved tasks  4 Ask task agent  5 List  6 Overdue  7 Summary  0 Exit')
        choice = input('Choose: ').strip()
        try:
            if choice == '0':
                break
            if choice == '1':
                print('Paste meeting notes. End with a line containing only END:')
                lines = []
                while (line := input()) != 'END':
                    lines.append(line)
                print(coordinator.analyze('\n'.join(lines)))
            elif choice == '2':
                print(coordinator.preview())
                idx = int(input('Item number (starting from 1): ')) - 1
                pic = input('PIC (blank = unchanged): ').strip() or None
                deadline = input('Deadline YYYY-MM-DD (blank = unchanged): ').strip() or None
                print(coordinator.clarify(idx, pic, deadline))
            elif choice == '3':
                print(coordinator.preview())
                if input('Save complete tasks? (yes/no): ').strip().lower() == 'yes':
                    print(coordinator.confirm_and_save())
            elif choice == '4':
                print(coordinator.command(input('Command: ')))
            elif choice == '5':
                print(list_tasks())
            elif choice == '6':
                print(check_overdue())
            elif choice == '7':
                print(task_summary())
            else:
                print('Unknown option')
        except (ValueError, RuntimeError, ConnectionError, OSError) as error:
            print('Error:', error)

if __name__ == '__main__':
    main()
