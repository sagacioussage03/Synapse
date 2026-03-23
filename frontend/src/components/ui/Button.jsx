export default function Button({ variant = 'default', children, ...props }) {
  const classes = ['btn'];
  if (variant === 'primary') classes.push('btn-primary');
  if (variant === 'danger') classes.push('btn-danger');
  if (variant === 'ghost') classes.push('btn-ghost');

  return (
    <button className={classes.join(' ')} {...props}>
      {children}
    </button>
  );
}