"""
Flow to fetch, classify and export Telegram schedule messages.

Flow:
    FetchTelegramMessagesNode (fetch messages -> CSV)
        ↓
    GroupMessagesByWeekNode (group by week -> list of weekly CSV)
        ↓
    LabelScheduleMessagesNode (AsyncParallelBatchNode - classify each week in parallel)
        ↓
    ExportExcelNode (export to Excel)
"""
import asyncio
from pocketflow import AsyncFlow
from nodes import (
    FetchTelegramMessagesNode,
    GroupMessagesByWeekNode,
    LabelScheduleMessagesNode,
    ExportExcelNode,
)


def create_schedule_flow():
    """Create and return a flow to fetch, classify and export schedule messages.

    Flow structure:
        Fetch -> Group by Week -> Label (parallel) -> Export Excel
    """
    # Create nodes
    fetch_node = FetchTelegramMessagesNode()
    group_node = GroupMessagesByWeekNode()
    label_node = LabelScheduleMessagesNode(max_retries=3, wait=1)
    export_node = ExportExcelNode()

    # Connect nodes in sequence
    fetch_node >> group_node >> label_node >> export_node

    # Use AsyncFlow because LabelScheduleMessagesNode is async
    return AsyncFlow(start=fetch_node)


async def run_flow():
    """Run the schedule flow asynchronously."""
    shared = {
        # FetchTelegramMessagesNode output
        "telegram_messages_csv": None,

        # GroupMessagesByWeekNode output
        "weekly_messages": None,

        # LabelScheduleMessagesNode output
        "labeled_messages": None,
        "weekly_labeled_messages": None,
        "labeled_messages_yaml": None,

        # ExportExcelNode output
        "excel_output_path": None,
    }

    # Create and run the flow
    flow = create_schedule_flow()
    await flow.run_async(shared)

    return shared


def main():
    """Main entry point."""
    shared = asyncio.run(run_flow())

    print("\n=== Schedule Report ===")
    print(f"Excel output: {shared.get('excel_output_path')}")
    print(f"\nLabeled messages (YAML):\n{shared.get('labeled_messages_yaml')}")

    return shared


if __name__ == "__main__":
    main()