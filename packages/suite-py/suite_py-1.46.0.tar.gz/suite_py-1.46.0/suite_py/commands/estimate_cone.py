# -*- encoding: utf-8 -*-
from suite_py.lib import metrics
from suite_py.lib.handler.youtrack_handler import YoutrackHandler


class EstimateCone:
    def __init__(self, project, config, tokens):
        self._project = project
        self._config = config
        self._youtrack = YoutrackHandler(config, tokens)

    @metrics.command("estimate-cone")
    def run(self, issue: str, sprint_board: str, previous_sprints: int):
        remaining_story_points = self._sum_of_unresolved_descendant_story_points(issue)

        current_sprint = self._youtrack.get_current_sprint(sprint_board)
        sprints = self._youtrack.get_sprints(sprint_board)

        current_sprint_index = next(
            (
                index
                for index, sprint in enumerate(sprints)
                if sprint["id"] == current_sprint["id"]
            ),
            None,
        )

        recent_sprints = sprints[
            current_sprint_index - previous_sprints : current_sprint_index
        ]

        sprints_resolved_story_points = [
            self._youtrack.get_sprint_resolved_story_points(sprint_board, sprint["id"])
            for sprint in recent_sprints
        ]

        average_story_points_per_sprint = sum(sprints_resolved_story_points) / len(
            sprints_resolved_story_points
        )
        max_story_points_per_sprint = (
            max(sprints_resolved_story_points) or 1
        )  # Avoid division by zero
        min_story_points_per_sprint = (
            min(sprints_resolved_story_points) or 1
        )  # Avoid division by zero

        average_estimate = remaining_story_points / average_story_points_per_sprint
        best_estimate = remaining_story_points / max_story_points_per_sprint
        worst_estimate = remaining_story_points / min_story_points_per_sprint

        print(f"Remaining story points: {remaining_story_points}")

        print(f"Max story points per sprint: {max_story_points_per_sprint}")
        print(f"Average story points per sprint: {average_story_points_per_sprint:.2f}")
        print(f"Min story points per sprint: {min_story_points_per_sprint}")

        print(f"Average estimate: {average_estimate:.2f} sprints")
        print(f"Best estimate: {best_estimate:.2f} sprints")
        print(f"Worst estimate: {worst_estimate:.2f} sprints")

        print(f"Sprints resolved story points: {sprints_resolved_story_points}")

    def _sum_of_unresolved_descendant_story_points(self, _issue_readable_id):
        descendants = self._youtrack.get_issue_descendants(_issue_readable_id)

        descendants_digested = [
            {
                "id": descendant.get("idReadable"),
                "summary": descendant.get("summary"),
                "resolved": bool(descendant.get("resolved")),
                "story_points": next(
                    (
                        field["value"]
                        for field in descendant["customFields"]
                        if field["name"] == "Story Points"
                    )
                )
                or 0,
            }
            for descendant in descendants
        ]

        for descendant in descendants_digested:
            if not descendant["resolved"]:
                print(descendant)

        return sum(
            descendant["story_points"]
            for descendant in descendants_digested
            if not descendant["resolved"]
        )
