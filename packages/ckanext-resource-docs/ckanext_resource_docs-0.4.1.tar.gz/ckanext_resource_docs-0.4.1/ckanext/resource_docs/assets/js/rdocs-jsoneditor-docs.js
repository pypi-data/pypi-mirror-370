ckan.module("rdocs-jsoneditor-docs", function ($, _) {
    "use strict";

    return {
        options: {
            resourceId: null,
            docsPrepopulate: {},
            submitBtnSelector: "#save-docs",
            schemaContainerSelector: "#jsoneditor-schema",
            docsContainerSelector: "#jsoneditor-docs"
        },
        initialize: function () {
            $.proxyAll(this, /_/);

            if (!this.options.resourceId) {
                return console.error("Resource ID is required to load resource docs.");
            }

            this.changed = false;
            this.validationSchema = {};

            // event bindings
            document.querySelector(this.options.submitBtnSelector).addEventListener("click", this._onDocumentationSave)

            // init JSONEditor
            this._loadResourceDocs();
            this._toggleSubmitButton(false);
        },

        _loadResourceDocs: function () {
            var self = this;

            this.sandbox.client.call(
                "GET",
                "resource_docs_show",
                `?resource_id=${this.options.resourceId}`,
                function (data) {
                    const result = data.result || { docs: {}, validation_schema: {} };

                    if (data.success && result) {
                        self._renderDocsJsonEditor(result);
                        self._renderSchemaJsonEditor(result);
                    }
                },
                function (err) {
                    self._renderDocsJsonEditor({docs: self.options.docsPrepopulate} || {});
                    self._renderSchemaJsonEditor({});
                    self._toggleSubmitButton(true);
                }
            );
        },

        _renderDocsJsonEditor: function (resDocs) {
            var self = this;
            this.validationSchema = resDocs.validation_schema || {};

            const options = {
                mode: 'text',
                content: { json: resDocs.docs || {} },
                validator: this._createAjvValidator(resDocs.validation_schema || {}),
                onChange: (updatedContent, previousContent, { contentErrors, patchResult }) => {
                    self._toggleSubmitButton(contentErrors === undefined);
                }
            }

            window.JSONEditorDOCS = window.createJSONEditor({ target: document.querySelector(this.options.docsContainerSelector), props: options })
        },

        _createAjvValidator: function (validation_schema) {
            try {
                return window.createAjvValidator({
                    schema: validation_schema,
                    schemaDefinitions: {},
                    ajvOptions: { strict: false },
                    onCreateAjv: (_) => {
                        return new window.Ajv2020({ strict: false, allErrors: true });
                    }
                })
            } catch (err) {
                console.debug("Error creating AJV validator:", err.message);
                return null;
            }
        },

        _renderSchemaJsonEditor: function (resDocs) {
            var self = this;

            window.JSONEditorSCHEMA = window.createJSONEditor({
                target: document.querySelector(this.options.schemaContainerSelector),
                props: {
                    mode: 'text',
                    content: {
                        text: undefined,
                        json: resDocs.validation_schema || {},
                    },
                    onChange: function (updatedContent, previousContent, { contentErrors, patchResult }) {
                        if (contentErrors !== undefined) {
                            return;
                        }

                        if (updatedContent.text === "") {
                            updatedContent = {"text": "{}"}
                        }

                        self.validationSchema = toJSONContent(updatedContent).json || {};
                        let validator = self._createAjvValidator(self.validationSchema)

                        try {
                            window.JSONEditorDOCS.updateProps({ validator: validator })
                            self._toggleSubmitButton(true);
                        } catch (err) {
                            console.debug("Invalid JSON, do not use this schema: ", err.message);
                        }
                    }
                }
            })
        },

        _onDocumentationSave: function () {
            let errors = window.JSONEditorDOCS.validate();

            if (errors === undefined) {
                this._overrideResourceDocs();
            } else {
                this._toggleSubmitButton(false);
                return console.debug("Schema validation errors:", errors);
            }
        },

        _overrideResourceDocs: function () {
            let content = window.JSONEditorDOCS.get();

            if (!content.text) {
                content = {text: {}}
            }

            const docs = toJSONContent(content);
            const schema = this.validationSchema;
            var self = this;

            const payload = {
                resource_id: this.options.resourceId,
                docs: JSON.stringify(docs.json),
                validation_schema: JSON.stringify(schema)
            };

            this.sandbox.client.call(
                "POST",
                "resource_docs_override",
                payload,
                function (response) {
                    window.JSONEditorDOCS.update({ json: response.result.docs });
                    ckan.notify('', ckan.i18n._("Resource documentation saved successfully"), 'success');
                    self._toggleSubmitButton(false);
                },
                function (err) {
                    console.debug("Error overriding resource docs:", err);
                    ckan.notify('', ckan.i18n._("An error occurred while saving the documentation"), 'error');
                }
            );
        },

        _toggleSubmitButton: function (state) {
            const submitBtn = document.querySelector(this.options.submitBtnSelector);

            this.changed = state;

            if (state) {
                submitBtn.disabled = false;
            } else {
                submitBtn.disabled = true;
            }
        }
    }
});
