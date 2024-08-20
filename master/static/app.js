let app = new Vue({
  el: "#app",
  data: {
    currentViewPi: {},
    loadingDevices: false,
    increasingLens: false,
    decreasingLens: false,
    increasingExposureTime: false,
    decreasingExposureTime: false,
    view: "devices",
    pis: [],
    photos: false,
    vf: "",
    onion: "",
    onionVf: "",
    shutterLoading: false,
    shutterErrors: [],
    currentSave: "",
    showVideo: false,
  },
  // Done
  computed: {
    videoFeedUrl() {
      return this.currentViewPi.uuid
        ? `/api/${this.currentViewPi.uuid}/video_feed`
        : "";
    },
  },
  methods: {
    device(uuid) {
      return this.pis.filter((x) => x.uuid == uuid)[0];
    },
    startVideoStream() {
      this.showVideo = true;
      console.log("showVideo:", this.showVideo);
    },

    stopCamera() {
      if (this.currentViewPi.uuid) {
        this.showVideo = false;
        console.log("showVideo:", this.showVideo);
        axios
          .get(`/api/${this.currentViewPi.uuid}/stopcamera`)
          .then((r) => {
            console.log("Camera stopped successfully.");
          })
          .catch((error) => {
            console.error("Failed to stop the camera:", error);
            this.isStreaming = true; // Re-set the flag if there is an error
          });
      }
    },

    // Done
    increaseLens() {
      this.increasingLens = true;
      axios.get(`/api/${this.currentViewPi.uuid}/increaselens`).then((r) => {
        this.increasingLens = false;
      });
    },
    // Done
    decreaseLens() {
      this.decreasingLens = true;
      axios.get(`/api/${this.currentViewPi.uuid}/decreaselens`).then((r) => {
        this.decreasingLens = false;
      });
    },
    // Done
    increaseExposureTime() {
      this.increasingExposureTime = true;
      axios
        .get(`/api/${this.currentViewPi.uuid}/increaseexposuretime`)
        .then((r) => {
          this.increasingExposureTime = false;
        });
    },
    // Done
    decreaseExposureTime() {
      this.decreasingExposureTime = true;
      axios
        .get(`/api/${this.currentViewPi.uuid}/decreaseexposuretime`)
        .then((r) => {
          this.decreasingExposureTime = false;
        });
    },

    TakePhotos() {
      this.photos = true;
      axios.get(`/api/trigger_capture`).then((r) => {
        this.photos = false;
      });
    },
    // Done
    reloadDevices: function () {
      this.loadingDevices = true;
      axios
        .get("/api/refresh")
        .then((r) => {
          this.pis = r.data;
        })
        .catch(() => {})
        .then(() => {
          this.loadingDevices = false;
        });
    },
    viewPi: function (pi) {
      this.currentViewPi = pi;
      this.view = "view";
    },
    rebootDevices: function () {
      axios.get("/api/reboot/all");
    },
    rebootDevice: function (pi) {
      axios.get("/api/" + pi.uuid + "/reboot");
    },
    cpip: function (ip) {
      copyStringToClipboard(ip);
    },
  },

  watch: {
    view(newView, oldView) {
      if (oldView === "view" && newView !== "view") {
        this.showVideo = false; // Reset showVideo flag
        this.stopCamera();
      }
    },
  },
  mounted: function () {
    this.reloadDevices();
  },
});
