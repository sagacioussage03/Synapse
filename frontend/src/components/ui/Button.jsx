import React from 'react';

export default function Button({ variant = 'default', children, ...props }) {
  const classes = ['btn'];
  if (variant === 'primary') classes.push('btn-primary');
  return (
    <button className={classes.join(' ')} {...props}>
      {children}
    </button>
  );
}