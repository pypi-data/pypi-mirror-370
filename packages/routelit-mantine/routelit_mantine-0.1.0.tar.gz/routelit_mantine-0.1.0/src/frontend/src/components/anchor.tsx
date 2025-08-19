import { Anchor as MantineAnchor, AnchorProps as MantineAnchorProps } from "@mantine/core";
import { useLinkClickHandler } from "routelit-client";

type AnchorProps = MantineAnchorProps & Parameters<typeof useLinkClickHandler>[0] & {
  text?: string;
};

export const Anchor = ({
  href,
  text,
  isExternal,
  children,
  id,
  replace,
  ...props
}: AnchorProps) => {
  const handleClick = useLinkClickHandler({ id, href, replace, isExternal});
  return (
    <MantineAnchor
      href={href}
      {...props}
      onClick={handleClick}
    >
      {text || children}
    </MantineAnchor>
  );
};

export default Anchor;
