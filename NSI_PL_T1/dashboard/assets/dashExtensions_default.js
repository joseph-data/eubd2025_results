window.dashExtensions = Object.assign({}, window.dashExtensions, {
    default: {
        function0: function(feature, context) {

            const {
                classes,
                colorscale,
                style,
                colorProp
            } = context.hideout; // get props from hideout

            const value = feature.properties[colorProp]; // get value the determines the color

            for (let i = 0; i < classes.length; ++i) {

                if (value > classes[i]) {

                    style.fillColor = colorscale[i];

                }

            }

            return style;

        },
        function1: function(feature, context) {

            const value = feature.properties["style"]; // get value the determines the color



            return value;

        }
    }
});