# Product Return Request (Odoo 18)

Custom module that lets internal users create return requests against confirmed
sale orders, submit them, and have them approved or rejected by a dedicated
"Return Manager" group.

## Install Steps

1. Copy the `sale_return_request` folder into your Odoo 18 `addons` path.
2. Restart the Odoo server.
3. Go to **Apps**, remove the "Apps" filter, search for **Product Return Request**.
4. Click **Install**.
5. Go to **Settings > Users**, open a user, and add them to the **Return Manager**
   group (under the Sales section) if they should be allowed to approve/reject
   return requests.

## Where to find it

Sales app > **Return Requests** menu.
Also visible from any confirmed Sale Order as a smart button ("Returns") in the
top-right corner of the form.

## Assumptions Made

- The requirement mentions filtering sale orders in **"sale or done"** state.
  Odoo 18 (since v15) no longer has a `done` state on `sale.order` — it was
  replaced by the `locked` flag. Since there is no `done` state to filter on,
  the module only filters on `state = 'sale'` (confirmed orders).
- "Regular internal users" is interpreted as users with standard Sales access
  (the `sales_team.group_sale_salesman` group). They can create and submit
  return requests but cannot approve/reject unless they are also in the
  **Return Manager** group.
- Approve/Reject are restricted both at the UI level (button `groups`
  attribute) and inside the Python methods (`has_group` check), so the
  restriction still holds even if called from outside the form view.
- Deletion is blocked in Python (`unlink` override) once a request leaves the
  `draft` state, as required. Access rights themselves still grant delete
  permission; the state check is what actually enforces the rule.
- "Delivered quantity" is read from `sale.order.line.qty_delivered`, which is
  the standard Odoo field for quantity delivered to the customer.
- The quantity check is implemented with `@api.constrains` (not just an
  `onchange`) so it is enforced on every create/write regardless of where the
  record is created from (form, import, API), not only from the UI form.

## Bonus Items Included

- Default search filters for each state (Draft/Submitted/Approved/Rejected).
- Group-by filters for Customer, Status, and Month (monthly-grouped list).
