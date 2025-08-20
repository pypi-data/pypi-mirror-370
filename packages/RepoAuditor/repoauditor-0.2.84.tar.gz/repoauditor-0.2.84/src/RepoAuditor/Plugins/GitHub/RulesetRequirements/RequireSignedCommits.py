# -------------------------------------------------------------------------------
# |
# |  Copyright (c) 2024 Scientific Software Engineering Center at Georgia Tech
# |  Distributed under the MIT License.
# |
# -------------------------------------------------------------------------------
"""Contains the RequireSignedCommits object."""

import textwrap

from RepoAuditor.Plugins.GitHub.Impl.EnableRulesetRequirementImpl import EnableRulesetRequirementImpl


class RequireSignedCommits(EnableRulesetRequirementImpl):
    """Check that the "Require signed commits" rule is disabled."""

    def __init__(self) -> None:
        super().__init__(
            name="RequireSignedCommitsRule",
            enabled_by_default=True,
            dynamic_arg_name="no",
            github_ruleset_type="required_signatures",
            github_ruleset_value="Require signed commits",
            get_configuration_value_func=self._GetValue,
            rationale=textwrap.dedent(
                """\
                The default behavior is to require signed commits. Note that this setting does not work with
                rebase merging or squash merging.

                Reasons for this Default
                ------------------------
                - Ensure that the author of a commit is who the claim to be.

                Reasons to Override this Default
                --------------------------------
                - You have enabled rebase merging or squash merging.
                """,
            ),
        )
