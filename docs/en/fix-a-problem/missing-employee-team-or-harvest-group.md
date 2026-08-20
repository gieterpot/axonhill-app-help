---
title: Employee, Team or Harvest Group is missing
flow_id: HR-10,HR-11,HR-12,HR-13,HR-14,HR-15
status: draft
reviewed: 2026-08-20
---

# Employee, Team or Harvest Group is missing

<p class="guide-meta">Draft. The current selector rules are verified. Final result checks still use the controlled test records.</p>

Use this when a person, Team or Harvest Group does not appear in an assignment or count form.

## First checks

1. Make sure the device has an internet connection.
2. Sync the app.
3. Close the form and open it again.
4. Check that you selected the correct request type.

## Harvest Group is missing

| What you see | Likely cause | What to do |
|---|---|---|
| A Team is selected, but the group is missing | The list is showing active groups for that Team only. | Check the Team. Ask the office to check that the Harvest Group is active and belongs to that Team. |
| Team is blank | The list should show all active Harvest Groups. | Search by the full group label and select the correct Team and operator combination. |
| The group is inactive | Inactive groups are not offered for new assignments. | Ask an administrator to confirm whether the group should be active. |

## Employee is missing

| Request type | Who should appear | What to check |
|---|---|---|
| **Add Additional Assignment** or **Move Assignment** | Active employees | Check that the employee is marked active. |
| **Remove Assignment** | Employees with an active Team membership | Check that the employee still has the assignment you intend to remove. |
| **Replace Chainsaw Operator** | Active employees whose default role is **Chainsaw Operator** | Check the default role and confirm that the operator is already an active member of the target Team. The current selector does not enforce the Team check. |
| **Change Harvest Group Role** | Current members of the selected Harvest Group | Open the member from the correct group before starting the request. |

Do not select **New** in a dropdown to work around a missing record. That can create a duplicate or incomplete employee, role or Harvest Group.

For Field attendance, a Supervisor must also have an active membership in the Team. Merely selecting that employee in the Team's Supervisor field does not make the Team appear in **Start Day**.

## Role is blank or rejected

Every added, moved or changed Harvest Group membership needs **With this role**. Choose the role before saving.

If processing fails, open the request and copy the full **Message**. Send the request type, employee, Team, Harvest Group and message to the administrator.
