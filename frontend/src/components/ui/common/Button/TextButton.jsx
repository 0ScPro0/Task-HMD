import { Button } from "./Button";

export function TextButton({font, width, height, fontSize, children, style, ...props}) {
    const textStyle = {
        fontFamily: font,
        fontSize: fontSize,
        ...style
    };

    return (
        <Button 
            {...props} 
            width={width} 
            height={height} 
            style={textStyle}
        >
            {children}
        </Button>
    )
}