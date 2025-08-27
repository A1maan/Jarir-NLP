import { useState, useRef, useCallback } from 'react';

/**
 * A custom hook to make an element draggable.
 * @param {React.RefObject<HTMLElement>} dragRef - A ref to the draggable element.
 * @returns {{position: {x: number, y: number}, onMouseDown: function}} - The position and event handler.
 */
export const useDraggable = (dragRef) => {
  const [position, setPosition] = useState({ x: 0, y: 0 });
  const isDraggingRef = useRef(false);
  const offsetRef = useRef({ x: 0, y: 0 });

  const handleMouseMove = useCallback((e) => {
    if (!isDraggingRef.current || !dragRef.current) return;

    e.preventDefault();
    e.stopPropagation();

    requestAnimationFrame(() => {
      const newX = e.clientX - offsetRef.current.x;
      const newY = e.clientY - offsetRef.current.y;

      const maxX = window.innerWidth - dragRef.current.offsetWidth;
      const maxY = window.innerHeight - dragRef.current.offsetHeight;

      const constrainedX = Math.max(0, Math.min(newX, maxX));
      const constrainedY = Math.max(0, Math.min(newY, maxY));

      dragRef.current.style.left = `${constrainedX}px`;
      dragRef.current.style.top = `${constrainedY}px`;
      dragRef.current.style.right = 'auto';
      dragRef.current.style.bottom = 'auto';
    });
  }, [dragRef]);

  const handleMouseUp = useCallback(() => {
    if (dragRef.current) {
      const finalX = parseFloat(dragRef.current.style.left) || 0;
      const finalY = parseFloat(dragRef.current.style.top) || 0;
      setPosition({ x: finalX, y: finalY });
    }
    
    isDraggingRef.current = false;
    document.body.style.userSelect = '';
    document.body.style.cursor = '';
    
    document.removeEventListener('mousemove', handleMouseMove);
    document.removeEventListener('mouseup', handleMouseUp);
  }, [dragRef, handleMouseMove]);

  const onMouseDown = useCallback((e) => {
    if (!dragRef.current) return;

    e.preventDefault();
    e.stopPropagation();

    const rect = dragRef.current.getBoundingClientRect();
    offsetRef.current = {
      x: e.clientX - rect.left,
      y: e.clientY - rect.top,
    };

    isDraggingRef.current = true;
    document.body.style.userSelect = 'none';
    document.body.style.cursor = 'grabbing';
    
    document.addEventListener('mousemove', handleMouseMove, { passive: false });
    document.addEventListener('mouseup', handleMouseUp);
  }, [dragRef, handleMouseMove, handleMouseUp]);

  return { position, onMouseDown };
};
