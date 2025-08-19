import {
  NavLink as MantineNavLink,
  NavLinkProps as MantineNavLinkProps,
} from "@mantine/core";
import { useLinkClickHandler } from "routelit-client";

type NavLinkProps = MantineNavLinkProps &
  Parameters<typeof useLinkClickHandler>[0] & {
    text?: string;
    exact?: boolean;
  };

export const NavLink = ({
  href,
  isExternal,
  id,
  replace,
  exact,
  ...props
}: NavLinkProps) => {
  const handleClick = useLinkClickHandler({ id, href, replace, isExternal });
  const isActive = exact ? href === window.location.pathname : window.location.pathname.startsWith(href);
  return (
    <MantineNavLink id={id} href={href} {...props} onClick={isExternal ? undefined : handleClick} active={isActive} />
  );
};

export default NavLink;
