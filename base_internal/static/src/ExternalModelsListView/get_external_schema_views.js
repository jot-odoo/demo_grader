/** @odoo-module **/

import { registry } from "@web/core/registry";
import { useOpenGetExternalSchemaButton } from "./get_external_schema_hook";
import { ListController } from "@web/views/list/list_controller";
import { listView } from "@web/views/list/list_view";

export class GetExternalSchemaListController extends ListController {
    setup() {
        super.setup();
        useOpenGetExternalSchemaButton();
    }
}

registry.category("views").add("get_external_schema_tree", {
    ...listView,
    Controller: GetExternalSchemaListController,
    buttonTemplate: "GetExternalSchema.buttons",
});
