import React, { Suspense, useMemo } from 'react';
import { IconLoader, IconFileUnknown } from '@tabler/icons-react'; // Fallback icons


/**
 * DynamicTablerIcon is a component that loads and displays Tabler icons dynamically.
 * It uses React.lazy to load the icons and Suspense to handle loading states.
 *
 * @param name - The name of the icon to load.
 * @param props - The props to pass to the icon.
 * @returns The icon component.
 * @example
 * <DynamicTablerIcon name="home" size={24} color="blue" />
 * <DynamicTablerIcon name="activity" size={32} />
 */
function DynamicTablerIcon({ name, ...props }: React.ComponentProps<typeof IconLoader>) {
  const LazyIcon = useMemo(() => {
    if (!name) {
      return null;
    }

    // Convert iconName (e.g., "Home") to "IconHome" for the import path
    const formattedIconName = name.startsWith("Icon") ? name : `Icon${name.charAt(0).toUpperCase() + name.slice(1)}`;

    return React.lazy(() =>
      // icon path might be `@tabler/icons-react/dist/esm/icons/${formattedIconName}.mjs`
    // @ts-expect-error - This is a workaround to get the icon name from the module
    import(`@tabler/icons-react`).then((module) => {
      const Icon = module[formattedIconName];
      if (Icon) {
        return { default: Icon };
      } else {
        console.warn(`Tabler Icon "${formattedIconName}" not found.`);
        return { default: IconFileUnknown }; // Fallback for not found icons
      }
    }).catch((error) => {
        console.error(`Error loading icon "${formattedIconName}":`, error);
        return { default: IconFileUnknown }; // Fallback on error
      })
    );
  }, [name]);

  if (!LazyIcon) {
    return null;
  }

  return (
    <Suspense fallback={<IconLoader className="animate-pulse" aria-label="Loading icon..." />}>
      <LazyIcon {...props} />
    </Suspense>
  );
}

export default DynamicTablerIcon;
