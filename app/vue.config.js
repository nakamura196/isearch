module.exports = {
  css: {
    loaderOptions: {
      css: {
        sourceMap: process.env.NODE_ENV !== "production" ? true : false
      }
    }
  },
  publicPath: "./",
  assetsDir: "static",
  outputDir: "../docs/app"
};
