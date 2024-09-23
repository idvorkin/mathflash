console.log("keyboard_capture.js++");
function registerPlugin(ctx) {
  // https://docs.hyperdiv.io/extending-hyperdiv/plugins#the-plugin-context-object
  version = "0.0.4";

  console.log("registerPlugin++ v:", version);
  console.log(ctx);
  // https://craig.is/killing/mice#api.bind
  Mousetrap.reset(); // For now we only support a single set of captures
  Mousetrap.bind(ctx.initialProps["capture"], (e) => {
    console.log(e);
    ctx.updateProp("last_pressed", e.key);
    ctx.updateProp("pressed_event", e.key);
  });
  console.log("registerPlugin--");

  ctx.onPropUpdate((propName, propValue) => {
    console.log("onPropUpdate++", propName, propValue);
  });
}
window.hyperdiv.registerPlugin("keyboard_capture", registerPlugin);
console.log("keyboard_capture.js--");
