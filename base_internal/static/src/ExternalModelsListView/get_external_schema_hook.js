/** @odoo-module **/

import { useService } from "@web/core/utils/hooks";

const { useComponent } = owl;

export function useOpenGetExternalSchemaButton() {
    const component = useComponent();
    const action = useService("action");

    component.onClickGetExternalSchema = () => {
        action.doAction({
            name: "Get External Schema",
            type: "ir.actions.act_window",
            res_model: "external.get.schema",
            target: "new",
            views: [[false, "form"]],
            context: { is_modal: true },
        });
    };
}
