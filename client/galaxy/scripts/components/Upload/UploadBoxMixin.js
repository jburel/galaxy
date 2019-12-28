import _l from "utils/localization";
import $ from "jquery";
import Select2 from "components/Select2";
import Popover from "mvc/ui/ui-popover";
import UploadExtension from "mvc/upload/upload-extension";
import UploadModel from "mvc/upload/upload-model";
import UploadWrapper from "./UploadWrapper";

export default {
    components: {
        UploadWrapper,
        Select2
    },
    props: {
        app: {
            type: Object,
            required: true
        }
    },
    methods: {
        initUploadbox(options) {
            const $uploadBox = $(this.$refs.wrapper.$refs.uploadBox);
            this.uploadbox = $uploadBox.uploadbox(options);
        },
        $uploadTable() {
            return $(this.$refs.uploadTable);
        },
        initExtensionInfo() {
            $(this.$refs.footerExtensionInfo)
                .on("click", e => {
                    new UploadExtension({
                        $el: $(e.target),
                        title: this.select_extension.text(),
                        extension: this.select_extension.value(),
                        list: this.list_extensions,
                        placement: "top"
                    });
                })
                .on("mousedown", e => {
                    e.preventDefault();
                });
        },
        initCollection() {
            this.collection = new UploadModel.Collection();
        },
        initAppProperties() {
            this.listExtensions = this.app.listExtensions;
            this.listGenomes = this.app.listGenomes;
            this.ftpUploadSite = this.app.currentFtp();
        },
        initFtpPopover() {
            // add ftp file viewer
            this.ftp = new Popover({
                title: _l("FTP files"),
                container: $(this.$refs.btnFtp)
            });
        },
        /* walk collection and update un-modified default values when globals
           change */
        updateExtension(extension, defaults_only) {
            this.collection.each(model => {
                if (
                    model.get("status") == "init" &&
                    (model.get("extension") == this.app.defaultExtension || !defaults_only)
                ) {
                    model.set("extension", extension);
                }
            });
        },
        updateGenome: function(genome, defaults_only) {
            this.collection.each(model => {
                if (
                    model.get("status") == "init" &&
                    (model.get("genome") == this.app.defaultGenome || !defaults_only)
                ) {
                    model.set("genome", genome);
                }
            });
        }
    }
};
