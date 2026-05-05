import styles from "./Button.module.css";

export function Button({name, width, height, children, onClick, style, ...props}) {

    const handleClick = (event) => {
        console.log(`${name} was pressed`);
        onClick?.(event);
    };

    const buttonStyle = height || width ? {
        width: width,
        height: height,
        ...style
    } : style;

    return (
        <div 
            className={styles.button} 
            role="button"
            style={buttonStyle}
            onClick={handleClick}
            {...props}
        >
            {children}
        </div>
    )
}
