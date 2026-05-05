import { Button } from "./Button";

export function ImageButton({ 
    src, 
    width,
    height, 
    img_width,
    img_height,
    children, 
    img_style = {},
    img_class_name = '', 
    onClick,
    ...props 
}) {
    
    return (
        <Button width={width} height={height} onClick={onClick} {...props}>
            <img 
                src={src} 
                width={img_width} 
                height={img_height} 
                alt="ico"
                style={{ 
                    display: 'block',
                    ...img_style  
                }}
                className={img_class_name}
            />
            {children}
        </Button>
    );
}